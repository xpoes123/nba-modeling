Deep-dive analysis on a specific game to understand why the model predicted what it did.

Usage: `/analyze-game YYYY-MM-DD AWAY HOME`
Example: `/analyze-game 2026-03-21 GSW ATL`

**IMPORTANT: Use a subagent for all DB queries and computation. Do not run queries inline.**

---

## Steps

**1. Parse the arguments** from the user's command (date, away team abbrev, home team abbrev).

**2. Launch a general-purpose subagent** with the following task. Pass the date and team names
   as part of the prompt. The subagent should write its full findings to
   `memory/game-analyses/YYYY-MM-DD-AWAY-HOME.md`.

The subagent prompt should include:

```
You are analyzing why our NBA prediction model predicted a specific game the way it did.
Use PYTHONPATH=. uv run python to run DB queries against db/nba_ratings.db.

IMPORTANT — Roster rules:
- Read memory/rosters.md FIRST before any analysis. It contains known team discrepancies,
  trades, and suspensions that are NOT in Claude's training data.
- Never state a player's team from internal knowledge. Use the DB players.team_id and rosters.md.
- If a player's team is unclear or not in rosters.md, note it as "unknown — ask David" in the analysis.
- Do not guess at injuries, trades, or suspensions outside what the DB and rosters.md confirm.

Game: {AWAY} @ {HOME} on {DATE}

Steps:
1. Find the game_id: SELECT game_id FROM games WHERE game_date='{DATE}' AND (home_team_id=... OR ...)
2. Pull stored prediction from predictions table for this game
3. Find both team IDs from the games table
4. Get the last-15-game lineup profiles for each team (before game_date) using the possession
   history (_get_team_possession_profiles logic from downstream/predictions.py)
5. Show each player's: name, games in window, eff_share, offense, defense, overall from current_ratings
6. Mark which players were OUT (from ESPN injury filter — check stored home_coverage/away_coverage
   to infer who was excluded, or note that Porzingis/Moody/etc. are known DNPs for that date)
7. Compute the exact raw_margin using team_ratings.compute_raw_margin formula:
     home_ppp = league_avg_ppp + (home_off - away_def) / 100
     away_ppp = league_avg_ppp + (away_off - home_def) / 100
     raw = (home_ppp - away_ppp) * expected_pace
8. Show the calibration math: alpha * raw + HCA + B2B adjustments = predicted_spread
9. Identify the top 2-3 reasons the model over- or under-predicted
10. Note any players missing from the 15-game window (long-term injuries not caught by ESPN)

Write ALL findings to memory/game-analyses/{DATE}-{AWAY}-{HOME}.md in this format:

# Game Analysis: {AWAY} @ {HOME}, {DATE}

## Stored Prediction
- Our spread: X | Market: Y | Edge: Z
- Coverage: home X% | away Y%
- B2B: home=T/F | away=T/F

## Team Lineup Profiles (last 15 games)

### HOME
| Player | Games | Share | OFF | DEF | Overall | Status |
...
Team OFF=X  DEF=Y  Net=Z

### AWAY
| Player | Games | Share | OFF | DEF | Overall | Status |
...
Team OFF=X  DEF=Y  Net=Z

## Raw Margin Math
home_ppp = ... | away_ppp = ... | raw_margin = ...
Calibrated: alpha * raw + adjustments = predicted

## Root Cause
1. ...
2. ...
3. ...

## Key Takeaways
- (what to learn about the model from this game)
```

**3. Read the written file** and give David a 3–5 sentence summary of the key findings.

**4. Append a one-line entry** to `memory/model-analysis.md` under the Prediction Log section
   with a link to the analysis file:
   ```
   ### {DATE} — {AWAY} @ {HOME} — [full analysis](game-analyses/{DATE}-{AWAY}-{HOME}.md)
   Our spread: X | Market: Y | Actual: Z | Root cause: [brief summary]
   ```

**Do not run DB queries yourself in the main context** — all computation goes through the subagent.

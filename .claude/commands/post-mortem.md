Post-game analysis for all games on a given date. Fully autonomous — no conversation. Appends findings to each game's analyze-game file.

Usage: `/post-mortem YYYY-MM-DD`
Example: `/post-mortem 2026-03-24`

**IMPORTANT: Use a subagent for all DB queries and computation. Do not run queries inline.**

---

## Phase 1 — Check for Missing Analyze-Game Files

Before doing anything, check which games on this date have predictions logged and which have analyze-game files:

1. Query: `SELECT game_id, home_team_id, away_team_id FROM games WHERE game_date='{DATE}'`
   Cross-reference with `predictions` table to find games we predicted on.
2. For each predicted game, check if `memory/game-analyses/{DATE}-{AWAY}-{HOME}.md` exists.

**If any predicted games are missing an analyze-game file:**
- List them explicitly to David: "Missing pre-game analysis for: [GAME1], [GAME2]"
- Instruct David: "Please run `/analyze-game {DATE} {AWAY} {HOME}` for each before re-running `/post-mortem {DATE}`"
- Stop here. Do not proceed until all files exist.

---

## Phase 2 — Gather Actuals (subagent)

Once all analyze-game files are confirmed, launch a general-purpose subagent with this task:

```
You are gathering post-game data for a set of NBA games on {DATE}.
Use: PYTHONPATH=. uv run python ... against db/nba_ratings.db
Use nba_api BoxScoreTraditionalV3 for actual box scores.
Return all data as structured text. Do NOT write any files.

For each predicted game on {DATE}:

1. Pull prediction data:
   SELECT p.*, g.home_score, g.away_score, g.home_team_id, g.away_team_id
   FROM predictions p JOIN games g ON p.game_id = g.game_id
   WHERE g.game_date = '{DATE}'

2. For each game compute:
   - actual_margin = home_score - away_score (positive = home won)
   - directional_result: did we pick the right winner? (sign of our_spread == sign of actual_margin)
   - ats_result: did our predicted side cover the market spread?
     e.g. if market = home -6 and actual_margin = +8, home covered ✓
     if market = home -6 and actual_margin = +4, home did NOT cover ✗
   - margin_error = our_spread - actual_margin
   - model_confidence_tier (from stored prediction)

3. For each game, pull actual box score using nba_api:
   from nba_api.stats.endpoints import BoxScoreTraditionalV3
   bs = BoxScoreTraditionalV3(game_id='{GAME_ID}')
   df = bs.player_stats.get_data_frame()[['playerName','minutes','points','assists','rebounds']]
   Return top 8 players by minutes for each team.

4. Day summary stats:
   - Total predicted games, games with outcomes resolved
   - Directional record (W-L), directional %
   - ATS record for HIGH tier only, for MODERATE tier only
   - Mean absolute error across all games
   - Mean absolute error for HIGH tier only
   - Biggest miss (game, our spread, actual margin, delta)
   - Biggest hit (game, our spread, actual margin, delta)

Return everything as structured text organized by game.
```

---

## Phase 3 — Append Post-Mortem to Each Analyze-Game File

For each game, read the existing `memory/game-analyses/{DATE}-{AWAY}-{HOME}.md` and append the following section at the bottom (after the `<!-- POST-MORTEM APPENDED BELOW -->` marker):

```markdown
---

## Post-Mortem

### Actual Outcome
- Final score: {AWAY} {AWAY_SCORE} @ {HOME} {HOME_SCORE}
- Actual margin: {HOME} {+/-N} (positive = home won)
- Our spread: {OUR_SPREAD} | Market: {MARKET_SPREAD} | Error: {MARGIN_ERROR:+.1f} pts

### Result
- Directional: {WIN/LOSS} — we predicted {SIDE} to win, they {DID/DID NOT}
- ATS: {COVER/NO COVER/PUSH} — market had {SIDE} -{LINE}, actual margin was {ACTUAL}

### Actual Box Score (top players by minutes)

**{HOME}**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
...

**{AWAY}**
| Player | Min | Pts | Reb | Ast |
|--------|-----|-----|-----|-----|
...

### Lineup Accuracy
- Compare top players in our profile vs. actual top-minutes players
- Flag anyone we had at high share who barely played, or anyone who played heavy minutes we didn't have
- Note if David's pre-game inputs (from Analyze-Game) turned out to be correct

### What the Model Got Right / Wrong
- [1-3 specific observations based on actual outcome vs. pre-game analysis]
- Reference any pre-game David inputs that were validated or contradicted
```

---

## Phase 4 — Day Summary to model-analysis.md

Append a day summary to `memory/model-analysis.md` under a new date header:

```markdown
### Post-Mortem: {DATE}
- Games: N predicted | Directional: W-L (X%) | HIGH ATS: W-L (X%) | MAE: X.X pts
- Biggest miss: {GAME} — predicted {OUR} actual {ACTUAL} (delta {DELTA})
- Biggest hit: {GAME} — predicted {OUR} actual {ACTUAL} (delta {DELTA})
- Notes: [any pattern worth flagging — e.g. "model undershooting home favorites again", "B2B picks went 0-2"]
- Full analyses: [link each game file]
```

---

## Phase 5 — Report to David

Give David a clean summary:
- Day record and key stats
- Which picks hit, which missed
- Any pattern worth investigating in a future session

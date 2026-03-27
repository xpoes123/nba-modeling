Deep-dive pre-game analysis on a specific game. Conversational — surfaces findings progressively and asks David to weigh in before writing the final file.

Usage: `/analyze-game YYYY-MM-DD AWAY HOME`
Example: `/analyze-game 2026-03-24 GSW DAL`

**IMPORTANT: Use a subagent for all DB queries and computation. Do not run queries inline.**

---

## Phase 1 — Data Gathering (subagent)

Launch a general-purpose subagent to gather all raw data. The subagent should NOT write any files or draw conclusions — just return structured data back to the main context.

Subagent prompt:

```
You are gathering raw data for a pre-game NBA model analysis. Return all data as structured text.
Do NOT write any files. Do NOT draw conclusions. Just pull the numbers.
Use: PYTHONPATH=. uv run python ... against db/nba_ratings.db

Game: {AWAY} @ {HOME} on {DATE}

1. Find the game_id: SELECT game_id, home_team_id, away_team_id FROM games
   WHERE game_date='{DATE}' AND home/away team matches

2. Pull stored prediction:
   SELECT * FROM predictions WHERE game_id='{GAME_ID}'
   (our_spread, market_spread, home_coverage, away_coverage, home_b2b, away_b2b, confidence_tier)

3. Get league_avg_ppp from league_averages WHERE season='2025-26'

4. For each team, get the last-15-game possession profiles before {DATE}:
   - Player name, player_id, games in window, raw possession share
   - offense, defense, overall from current_ratings

5. For each player in both profiles: flag if games_in_window < 5 (missing from window)

6. Compute team-level aggregates (weighted by share):
   - home_off, home_def, away_off, away_def

7. Compute raw_margin:
   home_ppp = league_avg_ppp + (home_off + away_def) / 100
   away_ppp = league_avg_ppp + (away_off + home_def) / 100
   raw_margin = (home_ppp - away_ppp) * expected_pace (use 100 if not available)

8. Show calibration math:
   Load downstream/calibration_coeffs.json
   predicted = alpha * raw_margin + HCA + (B2B_home if home_b2b) + (B2B_away if away_b2b)

Return all of this as structured text. No files, no conclusions.
```

---

## Phase 2 — Conversational Analysis

Once the subagent returns data, work through the findings with David section by section. Do NOT dump everything at once. Follow this order:

### 2a. Lineup profiles
Present each team's top players (by share) in a compact table. Then ask:
- For any player with games_in_window < 5: "Player X only appears in N of the last 15 games — do you know if they've been in/out of the rotation or injured?"
- For any player missing entirely from the window: "Player X isn't in our lineup profile at all — are they expected to play tonight?"
- For any coverage ratio below 80%: "Coverage is only X% for [TEAM] — the excluded players are [list]. Does that match tonight's injury report?"

Wait for David's response before continuing.

### 2b. Raw margin and calibration math
Show the step-by-step margin computation. Then ask:
- "Our model has [HOME] favored by [N] points. Does that directionally make sense for this matchup given what you know?"
- If home_b2b or away_b2b: "We're applying a B2B penalty to [TEAM] — do you know if their key players sat last night or played heavy minutes?"

Wait for David's response before continuing.

### 2c. Market comparison and edge
Show our spread vs. market spread and the edge. Then ask:
- If edge > 3 pts: "We have a [N]-point edge on [SIDE] — that's a significant gap. Any reason the market might be pricing this differently? (recent injuries, travel, matchup context we're missing?)"
- If our model is significantly softer than market (negative edge > 3): "The market has [TEAM] as much bigger favorites than we do — is there something we're missing about this team right now?"
- Always ask: "Any matchup-specific factors tonight that our model wouldn't capture? (style, pace, specific defensive assignments, rest advantage)"

Wait for David's response before continuing.

### 2d. Model bias check
Ask:
- "Are there any known model biases for either of these teams that we should flag? (teams we historically over/under-rate, style matchups we've missed before)"

---

## Phase 3 — Write the Analysis File

After the full conversation, write all findings + David's inputs to:
`memory/game-analyses/{DATE}/{AWAY}-{HOME}.md`

Format:

```markdown
# Game Analysis: {AWAY} @ {HOME}, {DATE}

## Stored Prediction
- Our spread: X | Market: Y | Edge: Z | Tier: T
- Coverage: home X% | away Y%
- B2B: home=T/F | away=T/F

## Team Lineup Profiles (last 15 games)

### {HOME}
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
...
Team OFF=X  DEF=Y  Net=Z

### {AWAY}
| Player | Games | Share | OFF | DEF | Overall | Notes |
|--------|-------|-------|-----|-----|---------|-------|
...
Team OFF=X  DEF=Y  Net=Z

## Raw Margin Math
home_ppp = ... | away_ppp = ... | raw_margin = ...
Calibrated: alpha * raw + HCA + B2B = predicted_spread

## David's Inputs
- [Capture everything David said during the conversation — rotation context, injury info, sanity checks, anything that confirms or challenges the model's assumptions]

## Pre-Game Assessment
- Model confidence: [tier + reasoning]
- Key risks: [top 2-3 things that could make this prediction wrong]
- Actionable? [Y/N and why]

---
<!-- POST-MORTEM APPENDED BELOW AFTER GAME COMPLETES -->
```

**4. Confirm with David** that the file looks right and nothing was missed before closing.

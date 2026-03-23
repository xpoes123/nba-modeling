# Spec: downstream/roster_report.py + /roster skill

**Status: NOT STARTED**
**Priority: Medium** — quality-of-life for game analysis; prevents Claude from using stale internal roster knowledge

## Background

Claude has been making incorrect claims about player team assignments (e.g. stating Zubac was on LAC when he'd been traded to Indiana) because internal training data is stale. `memory/rosters.md` is a manually-maintained fallback, but a live queryable script is more reliable. This script pulls from the DB + ESPN, giving Claude an accurate snapshot of any team's roster on demand.

## What to Build

### 1. `downstream/roster_report.py`

Standalone script. Takes `--team ABBR` or `--all`. Outputs a formatted ASCII table.

**Command:**
```bash
PYTHONPATH=. uv run python downstream/roster_report.py --team ATL
PYTHONPATH=. uv run python downstream/roster_report.py --team "Atlanta Hawks"
PYTHONPATH=. uv run python downstream/roster_report.py --all
```

**Output format:**
```
=== Atlanta Hawks (ATL) — Roster Report 2026-03-23 ===
  OFF    DEF   OVR   POSS%  STATUS   PLAYER
+2.24  -1.31  +3.55   19%           Dyson Daniels
+1.26  -0.61  +1.87   16%           Nickeil Alexander-Walker
+1.05  -0.76  +1.81   14%           CJ McCollum
...
+0.55  +0.21  +0.35    0%  [Q]      Jalen Johnson  (shoulder, Day-To-Day)
```

**Implementation steps:**

1. **Team resolution** — accept both abbreviation and full name:
   - Use `config.team_id_from_abbrev(abbrev.upper())`
   - Fall back to `config.team_id_from_name(name)` for full names
   - Error clearly if not found

2. **DB roster query:**
   ```sql
   SELECT p.player_id, p.player_name, cr.offense, cr.defense, cr.overall
   FROM players p
   JOIN current_ratings cr ON p.player_id = cr.player_id
   WHERE p.team_id = ?
   ```

3. **Recency-weighted possession shares** (replicate, don't import private fn):
   - Get last 15 game IDs: `SELECT game_id FROM games WHERE (home_team_id=? OR away_team_id=?) ORDER BY game_date DESC LIMIT 15`
   - For each game (slot 0 = most recent), weight = `0.85 ** slot`
   - Query possessions: `SELECT off_player_1..5 FROM possessions WHERE offense_team_id=? AND game_id=?`
   - Count appearances per player per game, multiply by game weight
   - Normalize weighted counts to shares (sum = 1.0)
   - Use `_RECENCY_DECAY = 0.85` (same as predictions.py)

4. **ESPN injury cross-reference:**
   - `from downstream.espn_client import get_nba_injuries`
   - Build lookup: `{normalize_name(inj['player_name']): inj}` for all injuries
   - `from downstream.team_ratings import normalize_name`
   - Match each DB player by normalized name

5. **Output:**
   - Sort by possession share DESC (most-used players first)
   - Players with share=0 (in DB but not in recent window, e.g. new arrivals or IR) shown at bottom
   - Status column: `[OUT]` if `is_out=True`, `[Q]` if `is_questionable=True`, blank otherwise
   - Include injury comment for OUT/Q players
   - Use `sys.stdout.buffer.write(...encode('utf-8'))` for non-ASCII names

6. **`--all` flag:** iterate `NBA_TEAM_MAP` (from config.py), print all 30 teams

### 2. `.claude/commands/roster.md`

Simple skill, no subagent needed — just a Bash call.

**Usage:** `/roster ATL` or `/roster "Memphis Grizzlies"`

**Skill content:**
```markdown
Get the current roster and injury report for a team from the DB + ESPN.

Run:
PYTHONPATH=. uv run python downstream/roster_report.py --team {TEAM}

Output shows: each player's offense/defense/overall ratings, recent possession share
(last 15 games, recency-weighted), and current ESPN injury status.

Use this whenever you need to know who is on a team, who is injured, or what a
team's rotation looks like. Never rely on internal knowledge — always run this script.
```

## Reusable Utilities (already exist — import these)

| Utility | Location |
|---------|----------|
| `team_id_from_abbrev(abbrev)` | `config.py` |
| `team_id_from_name(name)` | `config.py` |
| `NBA_TEAM_MAP` | `config.py` (team_id → {name, abbrev}) |
| `DB_PATH` | `config.py` |
| `get_nba_injuries()` | `downstream/espn_client.py` |
| `normalize_name(name)` | `downstream/team_ratings.py` |

## Verification

```bash
# Spot-check ATL: Dyson Daniels should be top, Jalen Johnson [Q]
PYTHONPATH=. uv run python downstream/roster_report.py --team ATL

# Spot-check MEM: Wells/Small should have high share; Morant/Edey/Bane NOT in possession window
PYTHONPATH=. uv run python downstream/roster_report.py --team MEM

# Spot-check PHI: Embiid/Maxey in DB but low share; Paul George NOT in DB (will not appear)
PYTHONPATH=. uv run python downstream/roster_report.py --team PHI

# All teams summary
PYTHONPATH=. uv run python downstream/roster_report.py --all
```

**Expected outputs:**
- MEM: Jaylen Wells and Javon Small at top; Morant/Edey/Bane absent (traded/long-term IR gone from window)
- PHI: bench players at top by share; Embiid/Maxey appear but with near-zero share + [OUT] flag
- ATL: Daniels at top; JJ with [Q] and shoulder note

## Notes
- No tests needed for this script (it's a reporting utility, not model logic)
- No changes to calibration_coeffs.json or any model file
- After implementation, run `/roster` for any game preview instead of guessing from internal knowledge
- Update `memory/rosters.md` to note that `roster_report.py` is now the primary tool

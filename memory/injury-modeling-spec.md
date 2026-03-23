# Injury Modeling Improvements — Implementation Spec

**Status:** Ready to implement
**Priority:** High — directly affects spread accuracy for games with injured/returning stars
**Authored:** 2026-03-23 (from analysis session)

---

## Problem Statement

The current lineup estimation has two complementary gaps:

### Gap A: Returning star has zero weight (under-representation)

When a player comes back from a long injury, they have few or zero appearances in the 15-game lookback window. The model treats them as if they don't exist, producing severely understated spread predictions.

**Example:** Steph Curry has 0 appearances in GSW's last 15 games (last played Dec 12-14, 2025). The model ignores him entirely — GSW's lineup looks like a mediocre team with Draymond Green (-3.25 ovr) as the anchor. Market has GSW -2.5 road favorites because the market knows Steph is returning soon.

### Gap B: Injured player contaminates the window (over-representation)

When a player has been out for several weeks but appeared in a handful of early-window games, their possession share inflates the team's apparent quality. Even though the ESPN injury filter excludes them from *tonight's* lineup, the historical games they played in skew the MinutesProfile and the baseline team rating before redistribution.

**Example:** Tyrese Maxey played 7 of PHI's last 15 games (before his current injury). PHI's MinutesProfile includes his positive influence on those 7 games. After the injury filter removes him tonight, the redistribution uses a starting point that was inflated by his presence. The net effect is PHI looks slightly better in our model than they really are with a fully-stripped roster.

---

## Proposed Fixes

### Fix A: Returning Player Pre-Seeding ← **DO THIS FIRST**

**What:** When a player is NOT on the ESPN injury list but has fewer than `N` appearances in the 15-game window AND has a strong `current_ratings` entry, inject them into the lineup at a discounted historical average.

**Why:** Their absence from the window is a data staleness artifact (long injury), not a reflection of their actual role on the team.

**Logic:**
1. After building the normal 15-game MinutesProfile, query all players with `current_ratings` for this team
2. For each player who is:
   - **Not** in `injured_names`
   - Has `< RETURNING_MAX_WINDOW_APPEARANCES` appearances in the 15-game window (e.g., 0–2)
   - Has `overall_rating >= RETURNING_THRESHOLD` (e.g., ≥ 2.0)
3. Query an extended lookback (last `RETURNING_EXTENDED_GAMES` = 30 games) to find their historical average possession share
4. If they appeared in `>= RETURNING_MIN_EXTENDED_APPEARANCES` games (e.g., 5) in the extended window:
   - Compute their recency-weighted average share from those historical games
   - Inject them into the MinutesProfile at `historical_share × RETURNING_MULTIPLIER` (e.g., 0.70)
5. After injecting all returning players, re-normalize the profile (coverage_ratio calculation is unchanged — returning players are NOT "injured" so they don't subtract from coverage)

**Constants to add to `config.py`:**
```python
RETURNING_PLAYER_THRESHOLD = 2.0          # min overall_rating to qualify
RETURNING_PLAYER_MAX_WINDOW_APPEARANCES = 2  # max appearances in 15-game window
RETURNING_PLAYER_EXTENDED_LOOKBACK = 30   # games to look back for historical share
RETURNING_PLAYER_MIN_EXTENDED_GAMES = 5   # min appearances in extended window to qualify
RETURNING_PLAYER_MULTIPLIER = 0.70        # discount on historical share (uncertainty discount)
```

**Files to modify:**
- `downstream/predictions.py` — `_build_minutes_profile_from_db()` and `_get_team_possession_profiles()`
- `config.py` — add constants above
- **NOT `downstream/backtest.py`** — backtest doesn't have live injury data and uses oracle rosters; returning player logic only applies to live predictions

**Notes:**
- Only applies in `predictions.py`, not `backtest.py` (backtest uses actual played rosters — no oracle needed)
- The `RETURNING_MULTIPLIER = 0.70` is a conservative starting point; tune it after backtest comparison
- A player who appears 0/15 in the window but 12/15 in games 16-30 is a strong "returning" signal
- This will affect `home_coverage` / `away_coverage` reporting — returning player injection should NOT lower coverage (they're active), but their injection effectively increases the profile's total weight. Decide: do we scale up or just add them in and renormalize? Recommendation: add them then renormalize — their injection means the profile is now "richer," not that someone is missing.

---

### Fix B: Hard Exclusion for Long-Term Injured Players ← **DO SECOND**

**What:** When a player is on the ESPN injury list AND missed the last `K` consecutive games (not just K of 15, but specifically the most recent K games), zero out their profile contribution rather than applying the standard availability discount.

**Why:** The availability discount (`games_appeared / total_games`) is symmetric — it doesn't distinguish between "missed every game for the last 3 weeks" and "missed every other game throughout the season." A player who hasn't played in the last 10 games straight should be treated as fully absent, not as a 33%-weight player.

**Logic:**
In `_build_minutes_profile_from_db()`:
1. After calling `_get_team_possession_profiles()`, also get the ordered list of game_ids (already returned from that function)
2. For each player in `profiles` who is in `injured_names`:
   - Walk the game_id list from most-recent to oldest
   - Count consecutive games the player DID NOT appear in at the start of the list
   - If `consecutive_recent_absences >= LONG_TERM_INJURY_STREAK` (e.g., 5):
     - Remove this player from `profiles` before the MinutesProfile is built (equivalent to weight=0, same as a player below `min_games`)
     - This player was already going to be removed by the injury filter — this just prevents their historical share from contaminating the coverage_ratio calculation

**Constants to add to `config.py`:**
```python
LONG_TERM_INJURY_STREAK = 5   # consecutive recent absences to trigger full exclusion
```

**Files to modify:**
- `downstream/predictions.py` — `_build_minutes_profile_from_db()`, needs consecutive-absence tracking from the profile data
- `config.py` — add constant above
- `downstream/backtest.py` — **also update** here for consistency, even though backtest doesn't use injury data (prevents asymmetry in what "counts" as a game)

**Implementation detail:** `_get_team_possession_profiles()` currently returns `player_shares` dict (only games where the player appeared). To detect consecutive absences, the function needs to also return the full ordered `game_ids` list. This is a minor signature change:

```python
# Current return
return player_shares, n_window_games

# Updated return
return player_shares, game_ids  # game_ids replaces n_window_games (can derive n from len)
```

All callers will need to be updated.

---

### Fix C (Future — separate session): Injury Timetable Integration

**What:** Ingest injury return-date estimates from a source (ESPN, rotowire, etc.) and use them to modulate how aggressively we apply Fix A.

**Why:** "Steph Curry is out 2 more weeks" should produce different behavior than "Steph Curry could return tomorrow." Currently both cases look identical to the model (0 appearances → inject at 70% of historical).

**Approach sketch:**
- Add a new table `injury_timetable` to the DB schema: `(player_id, as_of_date, expected_return_date, status_source)`
- The returning player injection uses `days_until_return` to scale the multiplier:
  - `return_tomorrow` → multiplier = 1.0 (full injection)
  - `return_in_5_days` → multiplier = 0.70
  - `return_in_15_days` → multiplier = 0.30
  - `return_unknown` → multiplier = 0.50 (default, same as current Fix A)
- Data source options: ESPN injury API (already integrated), rotowire (web scrape), or manual entry via a new CLI command

**This requires David's input on data source reliability before building.**

---

## Validation Plan

After implementing Fix A, run a backtest comparison to check impact:

```bash
# Before fix (run on current main)
PYTHONPATH=. uv run python downstream/backtest.py --start 2026-01-01 --end 2026-03-23

# After fix (on branch with returning player logic)
PYTHONPATH=. uv run python downstream/backtest.py --start 2026-01-01 --end 2026-03-23
```

Compare: MAE, corr, directional accuracy. Also manually check that today's GSW @ DAL prediction changes — Steph should now appear in GSW's MinutesProfile at ~70% of his historical average, making GSW look significantly stronger.

**Expected impact of Fix A:**
- Games where a star is returning: prediction moves toward market (less model-market gap)
- Teams where the star hasn't returned yet: no change (model behavior identical to current)
- Directional accuracy: expect modest improvement on "returning star" games; full-season impact small since these games are rare

**Expected impact of Fix B:**
- PHI-type games: slightly lower PHI team rating (Maxey's contribution removed more aggressively), OKC spread increases toward market
- MIL-type games: Giannis fully excluded from baseline before redistribution, MIL rating drops slightly
- Directional accuracy: marginal improvement; the injury filter already handles the "tonight" exclusion so the gain is subtle

---

## Files Touched Summary

| File | Fix A | Fix B |
|------|-------|-------|
| `config.py` | Add 5 constants | Add 1 constant |
| `downstream/predictions.py` | Modify `_build_minutes_profile_from_db()` | Modify same function + `_get_team_possession_profiles()` return signature |
| `downstream/backtest.py` | No change | Minor: update `_get_team_profiles()` return signature |
| `tests/test_predictions.py` | Add test cases for returning player injection | Add test for long-term exclusion |

---

## Tests to Add

```python
# Fix A: returning player injection
def test_returning_player_is_seeded_from_extended_window():
    # Player has 0/15 appearances, high rating, 10/30 in extended window
    # Expected: player appears in MinutesProfile at ~70% of extended average

def test_low_rated_returning_player_not_seeded():
    # Player has 0/15 appearances, ovr=0.5 (below threshold)
    # Expected: player NOT injected

def test_injured_returning_player_not_seeded():
    # Player has 0/15 appearances, high rating, BUT is on injured_names
    # Expected: player NOT injected

# Fix B: long-term exclusion
def test_long_term_injured_player_excluded():
    # Player has 7/15 appearances but missed last 6 consecutive games, and is on injured_names
    # Expected: player excluded from MinutesProfile (not just removed by injury filter)

def test_intermittent_dnp_player_not_excluded():
    # Player has 7/15 appearances scattered throughout window, not in injured_names
    # Expected: normal availability discount applies, player included
```

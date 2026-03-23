# NBA Roster Exceptions — 2025-26 Season

**Last updated: 2026-03-23 by David**

## How Claude should use this file
- Always read this before making any claim about a player's team, status, or availability
- If something is unclear or not listed here, **ask David — never assume**
- The DB `players.team_id` is the primary source for team assignments; this file documents known gaps and corrections

---

## Players with NULL team_id in DB (model blind spots)

These players won't appear in any team's lineup simulation. Their absence is a known model gap.

| Player | Actual Team | ESPN Status | Notes |
|--------|-------------|-------------|-------|
| Paul George | PHI | Suspended (25 games) | In `players` table, team_id=NULL; PHI lineup simulation doesn't include him |
| Damian Lillard | POR | Out (injury) | In `players` table, team_id=NULL, not in current_ratings |
| Trae Young | WAS | Out (injury) | team_id=NULL; was traded ATL→WAS |
| De'Andre Hunter | SAC | Out (injury) | team_id=NULL; was traded ATL→SAC |

---

## Known DB Team Discrepancies (DB stale vs actual current team)

| Player | DB team_id shows | Actual Team | ESPN Status | Notes |
|--------|-----------------|-------------|-------------|-------|
| Anthony Davis | DAL | WAS | Out | Traded DAL→WAS; DB not updated yet |

---

## Notable Trades Confirmed in DB (2025-26 season — not in Claude's training data)

The DB reflects these correctly. Listed here so Claude doesn't contradict them.

| Player | From | Current Team (DB) | Active? |
|--------|------|-------------------|---------|
| Desmond Bane | MEM | ORL | Active |
| Jaren Jackson Jr. | MEM | UTA | Out (injury) |
| Anfernee Simons | POR | CHI | Out |
| Michael Porter Jr. | DEN | BKN | Out |
| Jimmy Butler | MIA | GSW | Out |
| CJ McCollum | NOP | ATL | Active |
| Jonathan Kuminga | GSW | ATL | Active |
| Jrue Holiday | BOS | POR | Active |

---

## Tanking Teams 2025-26 (own their draft pick — incentivized to lose)

These teams have their draft picks and are tanking for lottery positioning. Apply a tanking penalty
to their spreads (feature not yet implemented — tracked as improvement item in model-analysis.md).

| Team | Notes |
|------|-------|
| Sacramento Kings | Tanking |
| Utah Jazz | Tanking — also gutted by injuries (see below) |
| Washington Wizards | Tanking |
| Brooklyn Nets | Tanking |

---

## Teams with Severely Depleted Rosters (context for spread analysis)

### Memphis Grizzlies
Out/season-ending: Ja Morant, Zach Edey, Santi Aldama, KCP, Scotty Pippen Jr., Brandon Clarke.
Also lost via trade: Desmond Bane (→ORL), Jaren Jackson Jr. (→UTA).
Active rotation led by Jaylen Wells (ovr=0.84) and Javon Small (ovr=0.54).
Model already reflects this — injured/traded players are absent from the 15-game possession window.

### Utah Jazz
Out: Lauri Markkanen, Keyonte George, Jusuf Nurkic, Walker Kessler, Jaren Jackson Jr. (now on UTA, also Out).
Nearly the entire starting lineup is unavailable.

### Philadelphia 76ers
Out/suspended: Joel Embiid, Tyrese Maxey, Paul George (suspended, NULL in DB), Kelly Oubre Jr.
Model reflects Embiid/Maxey absence (both rarely in 15-game window).
Paul George not in any lineup simulation.

### Detroit Pistons
Out: Cade Cunningham (collapsed lung). Primary ball-handler and best player on the team.
Explains 83% coverage on 2026-03-23 LAL @ DET — his possession share is redistributed to backups.

### Washington Wizards
Out: Anthony Davis (DB stale as DAL), Trae Young (NULL team), plus multiple others.

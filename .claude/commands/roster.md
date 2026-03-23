Get the current roster and injury report for a team from the DB + ESPN.

The user invoked this skill as: `/roster $ARGUMENTS`

Run:
```bash
PYTHONPATH=. uv run python downstream/roster_report.py --team $ARGUMENTS
```

Output shows: each player's offense/defense/overall ratings, recent possession share (last 15 games, recency-weighted), and current ESPN injury status.

Use this whenever you need to know who is on a team, who is injured, or what a team's rotation looks like. Never rely on internal knowledge — always run this skill.

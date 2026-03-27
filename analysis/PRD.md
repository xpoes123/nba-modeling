# PRD: Team Style Clustering & Matchup Analysis

**Status:** In Progress
**Owner:** David Jiang
**Created:** 2026-03-26
**Related:** `memory/model-analysis.md` (backlog item #9 — matchup-specific adjustments)

---

## 1. Motivation & Hypothesis

The current RAPM-based prediction model treats all opponents as "the average team." It computes
a raw margin based on player-weighted offensive and defensive ratings, then applies a global
calibration (HCA, B2B penalties). There are no matchup-specific adjustments.

**The hypothesis:** Certain team *style archetypes* systematically beat or lose to other
archetypes in ways that RAPM does not capture. Examples:

- **SAS/Wemby vs OKC** — Wembanyama's unique rim protection and switchability disrupts OKC's
  pick-and-roll-heavy, 3PT-spacing offense. OKC relies on SGA driving into the lane; Wemby erases
  that. This isn't fully captured in aggregate RAPM.
- **Fast transition teams vs disciplined halfcourt teams** — High-pace teams (MEM, OKC) may
  struggle against teams that slow the game down and force them into halfcourt sets.
- **3PT-heavy offenses vs physically imposing defenses** — Teams that survive on 3-point volume
  may face variance collapse against "paint-first" defensive schemes.

**The goal** is to:
1. Quantify these style archetypes using the data we have
2. Discover which cluster matchups show systematic model residuals
3. Provide a production-ready interface for downstream pipeline integration

---

## 2. Success Criteria

| Criterion | Target |
|-----------|--------|
| All 30 teams assigned a style cluster | ✓ complete assignment |
| PCA top 3 components explain variance | ≥ 65% |
| Clustering quality (silhouette score) | ≥ 0.30 |
| Number of identified style archetypes | 4–6 named clusters |
| Statistically significant cluster-pair edges | ≥ 2 pairs with \|mean residual\| > 4 pts and n ≥ 20 games |
| Production interface | `get_team_cluster()` matches notebook output for all 30 teams |
| Pipeline integration (if signal confirmed) | Calibration directional accuracy improves ≥ 1pp |

---

## 3. Data Sources

All data from `db/nba_ratings.db` (2025-26 season only).

| Table | Key Columns Used | Purpose |
|-------|-----------------|---------|
| `possessions` | `fg2a`, `fg2m`, `fg3a`, `fg3m`, `free_throw_points`, `points_scored`, `turnovers`, `offensive_rebounds`, `start_type`, `offense_team_id`, `defense_team_id` | All shooting, ball control, and transition features |
| `games` | `game_pace`, `home_team_id`, `away_team_id`, `home_score`, `away_score` | Pace feature + game outcomes for matchup analysis |
| `current_ratings` | `player_id`, `offense`, `defense`, `pace` | RAPM-based composition features |
| `players` | `player_id`, `team_id` | Team assignment for composition features |
| `config.NBA_TEAM_MAP` | team_id → abbreviation | Team labels in visualizations |

No external data needed for the core analysis. ESPN injury data is not used (purely structural/style features).

---

## 4. Feature Specification (18 Features)

All features are computed at the team level for the full 2025-26 season to date.

### 4a. Offensive Style (9 features)
Computed from `possessions` WHERE `offensive_team_id = team_id`:

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| `three_pt_attempt_rate` | `SUM(fg3a) / (SUM(fg2a) + SUM(fg3a))` | 3PT shot selection — high = spacing/perimeter offense |
| `three_pt_pct` | `SUM(fg3m) / SUM(fg3a)` | 3PT shooting efficiency |
| `two_pt_pct` | `SUM(fg2m) / SUM(fg2a)` | Paint/midrange efficiency |
| `ft_point_rate` | `SUM(free_throw_points) / SUM(points_scored)` | Free throw generation — high = physical/attacking style |
| `fga_per_possession` | `(SUM(fg2a) + SUM(fg3a)) / COUNT(*)` | Shot aggressiveness — low = more ball movement/passes |
| `turnover_rate` | `SUM(turnovers) / COUNT(*)` | Ball control — high = reckless or fast-paced |
| `oreb_rate` | `SUM(offensive_rebounds) / COUNT(*)` | Second-chance aggression — high = physical/big-man teams |
| `transition_rate` | `COUNT(*) FILTER (WHERE start_type LIKE '%Transition%') / COUNT(*)` | Fast-break frequency |
| `off_rating` | `SUM(points_scored) / COUNT(*) * 100` | Overall offensive efficiency per 100 possessions |

### 4b. Defensive Style (5 features)
Computed from `possessions` WHERE `defensive_team_id = team_id`:

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| `opp_three_pt_attempt_rate` | `SUM(fg3a) / (SUM(fg2a) + SUM(fg3a))` | Does defense force perimeter shots? |
| `opp_two_pt_pct` | `SUM(fg2m) / SUM(fg2a)` | Paint defense quality — low = rim protection |
| `opp_turnover_rate` | `SUM(turnovers) / COUNT(*)` | Defensive pressure / forced chaos |
| `opp_oreb_rate` | `SUM(offensive_rebounds) / COUNT(*)` | Opponents' second-chance rate vs us — low = good defensive rebounding |
| `def_rating` | `SUM(points_scored) / COUNT(*) * 100` | Overall defensive efficiency per 100 possessions |

### 4c. Pace (1 feature)
From `games` table, averaging across all games the team played:

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| `avg_pace` | `AVG(game_pace)` | Possessions per 48 min — the definitive pace metric |

### 4d. Player Composition (3 features)
From `current_ratings` × `players` × last-15-game possession shares (recency-weighted, same
methodology as `downstream/predictions.py:_build_minutes_profile_from_db()`):

| Feature | Formula | Interpretation |
|---------|---------|----------------|
| `weighted_off_rapm` | `Σ(player_offense × possession_share)` | Team's effective offensive RAPM (talent-weighted) |
| `star_concentration` | `Gini(possession_shares)` | 0 = perfectly balanced rotation, 1 = single player |
| `rotation_depth` | `COUNT(players with share > 8%)` | How many meaningful contributors |

**Note on defense sign convention:** `positive defense = BAD defender` throughout the codebase.
`weighted_def_rapm` is intentionally excluded from this feature set to avoid double-counting
with `def_rating` computed from actual possessions — the RAPM-based feature is noisier.

---

## 5. Deliverables & Phases

### Phase 1 — Feature Engineering
**File:** `analysis/01_features.ipynb`

Steps:
1. Connect to `db/nba_ratings.db` using `sqlite3`
2. SQL queries for all 9 offensive + 5 defensive + 1 pace features
3. Python computation for 3 player-composition features
4. Merge into 30×18 DataFrame; label rows with team abbreviations
5. Sanity checks (no NULLs, ranges within expected bounds — see Section 6)
6. Correlation heatmap of raw features
7. Export: `analysis/data/team_features.csv`

### Phase 2 — PCA Exploration
**File:** `analysis/02_pca.ipynb`

Steps:
1. Load `team_features.csv`, `StandardScaler` normalize (z-score)
2. Fit `sklearn.decomposition.PCA(n_components=18)`
3. Scree plot: bar chart of explained variance ratio + cumulative curve
4. Identify n_components that reaches 70% cumulative variance (expected: 3–5)
5. Biplot: PC1 vs PC2 axes, feature loading arrows, team labels overlaid
6. Attempt interpretation of each PC axis:
   - PC1 might separate "perimeter-heavy offense" vs "paint/physical offense"
   - PC2 might separate "fast/transition" vs "slow/halfcourt"
   - PC3 might separate "star-dependent" vs "depth-balanced"
7. Save normalized features: `analysis/data/team_features_normalized.csv`
8. Save PCA model: `analysis/data/pca_model.pkl`

### Phase 3 — Clustering
**File:** `analysis/03_clustering.ipynb`

Steps:
1. Load normalized features + PCA model
2. Project 30 teams into PCA space (top K components where K achieves 70% variance)
3. Sweep k=2..10:
   - Inertia (elbow method)
   - Silhouette score
   - Davies-Bouldin index
4. Select optimal k (target 4–6)
5. Fit final `KMeans(n_clusters=k, random_state=42, n_init=20)`
6. Visualize: scatter plot in PC1-PC2 space, colored by cluster, labeled by team abbreviation
7. Print cluster profiles table: each cluster's centroid values for all 18 raw features
8. Name clusters based on dominant feature loadings (e.g., "3PT Spacing + Pace", "Paint Defense + Slow")
9. David validates cluster names (ask him if labels make sense)
10. Save outputs:
    - `analysis/data/cluster_assignments.json` — `{"team_id": cluster_id, ...}` + `"cluster_names": [...]`
    - `downstream/cluster_model.pkl` — fitted KMeans object
    - `downstream/cluster_model_meta.json` — feature names, k, scaler params, cluster names

### Phase 4 — Matchup Analysis
**File:** `analysis/04_matchup_analysis.ipynb`

Steps:
1. Load cluster assignments from `analysis/data/cluster_assignments.json`
2. Run backtest across full season to get per-game predictions + actuals:
   - Use `downstream/backtest.py` logic or re-implement inline
   - For each game: predicted_margin (home), actual_margin (home_score - away_score)
3. For each game, assign `home_cluster` and `away_cluster`
4. Compute: `residual = actual_margin - predicted_margin`
   - Positive = model under-predicted home team (home actually won by more)
   - Negative = model over-predicted home team
5. Build k×k cross-tab grid:
   - Rows = home cluster, Cols = away cluster
   - Values: mean residual, n games, bootstrap 95% CI (1000 resamples)
   - Highlight cells where CI excludes 0 and n ≥ 15
6. Visualize: seaborn heatmap of mean residuals + overlay significance markers
7. Deep-dive on each significant pair:
   - List team matchups in that pair
   - Compute per-matchup residuals
   - Hypothesize the style mismatch
8. **Specific spotlight:** SAS (Wemby) vs OKC (SGA) matchup history
   - Assign clusters, compute H2H residuals, validate the "Wemby disrupts OKC" hypothesis
9. Write findings summary section at end of notebook
10. Save results: `analysis/data/matchup_residuals.csv`

### Phase 5 — Production Interface
**File:** `downstream/team_style.py`

```python
def compute_team_features(conn: sqlite3.Connection, team_id: str, season: str = "2025-26") -> dict[str, float]:
    """
    Compute all 18 style features for a single team.
    Returns raw (unnormalized) feature values.
    """

def get_team_cluster(conn: sqlite3.Connection, team_id: str, season: str = "2025-26") -> int:
    """
    Load the saved cluster model, compute + normalize features, return cluster ID (0-indexed).
    Raises FileNotFoundError if cluster_model.pkl has not been generated yet.
    """

def get_all_team_clusters(conn: sqlite3.Connection, season: str = "2025-26") -> dict[str, int]:
    """Return {team_id: cluster_id} for all 30 teams."""
```

The module loads `downstream/cluster_model.pkl` and `downstream/cluster_model_meta.json` at
import time (or lazily on first call). Feature computation uses the same SQL logic as the
notebooks — single source of truth.

### Phase 6 — Calibration Integration (Conditional)
**File:** `downstream/calibration.py` (modify only if signal confirmed)

Trigger conditions (ALL must be met):
- At least one cluster-pair has |mean residual| > 4 pts
- That cluster-pair has n ≥ 20 games
- Bootstrap 95% CI for the residual excludes 0
- Backtest shows directional accuracy improvement ≥ 1pp after adding the feature

If triggered:
1. Add `home_cluster` and `away_cluster` columns to calibration training data
2. Add `(home_cluster, away_cluster)` interaction dummy variables as OLS features
3. Refit OLS, apply EB shrinkage (same pattern as team HCA dummies)
4. Run full backtest before/after: compare MAE, val_corr, directional accuracy
5. Only update `calibration_coeffs.json` if improvement is confirmed
6. Update `config.py` with `N_CLUSTERS` constant

---

## 6. Validation & Sanity Checks

### Feature Range Validation (Phase 1)
| Feature | Expected Range |
|---------|---------------|
| `three_pt_attempt_rate` | 36% – 47% |
| `three_pt_pct` | 34% – 38% |
| `two_pt_pct` | 52% – 58% |
| `ft_point_rate` | 12% – 18% |
| `turnover_rate` | 11% – 18% |
| `oreb_rate` | 10% – 19% |
| `transition_rate` | 5% – 20% (check start_type values first) |
| `off_rating` | 107 – 122 pts/100 |
| `def_rating` | 107 – 122 pts/100 |
| `avg_pace` | 88 – 108 poss/48 |
| `star_concentration` | 0.10 – 0.50 |
| `rotation_depth` | 5 – 12 |

### PCA Validation (Phase 2)
- Top 3 PCs explain ≥ 65% of variance
- No single feature dominates all loading arrows on the biplot

### Clustering Validation (Phase 3)
- Silhouette score ≥ 0.30
- No cluster with fewer than 3 teams
- David validates cluster names make NBA sense

### Matchup Validation (Phase 4)
- Total residuals ≈ 0 (model is unbiased overall — calibration v5)
- Per-cluster residuals shouldn't exceed |10 pts| (extreme = overfitting)
- Cross-check: the SAS/OKC "Wemby disrupts" hypothesis should appear as a negative
  residual on the OKC-home side when SAS is visiting (OKC underperforms prediction)

---

## 7. File Map

```
analysis/
├── PRD.md                          ← this file
├── 01_features.ipynb               ← Phase 1
├── 02_pca.ipynb                    ← Phase 2
├── 03_clustering.ipynb             ← Phase 3
├── 04_matchup_analysis.ipynb       ← Phase 4
└── data/
    ├── .gitkeep
    ├── team_features.csv           ← output of Phase 1
    ├── team_features_normalized.csv
    ├── pca_model.pkl
    ├── cluster_assignments.json    ← output of Phase 3
    └── matchup_residuals.csv       ← output of Phase 4

downstream/
├── team_style.py                   ← Phase 5 (production interface)
├── cluster_model.pkl               ← saved by Phase 3 notebook
└── cluster_model_meta.json         ← feature names, k, cluster names
```

**Data directory note:** `analysis/data/` is in `.gitignore` for CSV/pickle files (generated
artifacts). Only `.gitkeep` and `.json` files are committed. `downstream/cluster_model.pkl`
IS committed — it's required for production predictions.

---

## 8. Architecture Decisions

### Why PCA before K-Means?
30 teams with 18 features is a small dataset. PCA reduces dimensionality AND removes
correlated features (e.g., `off_rating` and `three_pt_pct` are correlated) before K-Means,
which improves cluster quality and interpretability.

### Why current season only?
We have 1,080 games in the 2025-26 season — sufficient for stable team-level aggregates.
Adding historical seasons would require backfilling prior seasons' PBP data (significant effort)
and would conflate different rosters (e.g., OKC pre/post trade, GSW pre/post Curry injury).

### Why cluster-pair residuals rather than team-specific RAPM adjustments?
Matchup-specific RAPM would require fitting opponent interaction terms — with only 2–4 H2H
games per team pair, this overfits severely. Cluster-pair analysis pools across stylistically
similar teams (5×5 = 25 games per cluster pair on average), giving enough signal for inference.

### Why not use KNN for clustering?
The task is to group teams into archetypes (unsupervised), not to classify new data points
based on labeled examples. KNN is a supervised/classification algorithm. K-Means is the right
tool here. KNN is also mentioned in the original request but what's actually meant is K-Means
(unsupervised clustering).

---

## 9. Future Extensions

1. **Multi-season clustering** — Fit clusters on prior 3 seasons combined; assign current teams
   to clusters using same feature set. Larger sample for cluster-pair residuals.

2. **Lineup-level clustering** — Instead of team-level, cluster the top-8 lineup combinations
   for each team. Some teams have split identities (OKC with SGA is different from OKC without).

3. **Dynamic cluster tracking** — Recompute cluster assignments monthly as team compositions
   evolve (trades, injuries, development). Track if a team "drifts" clusters mid-season.

4. **Wemby interaction term** — Manually encode a `wemby_in_game` binary feature for the
   SAS matchups and test as a calibration feature independently.

5. **Opposition-specific RAPM** — Long-term: fit RAPM with (player_id, opponent_cluster)
   interaction terms using multi-season data. Would capture Wemby's cluster-specific impact.

---

## 10. Dependencies

All packages are already in `requirements.txt`:
- `scikit-learn` — PCA, KMeans, StandardScaler, silhouette_score
- `pandas`, `numpy` — data manipulation
- `matplotlib`, `seaborn` — visualization
- `sqlite3` — standard library, no install needed

New dependency (if not already present):
- `jupyter` / `notebook` — for running `.ipynb` files (`uv run jupyter notebook`)

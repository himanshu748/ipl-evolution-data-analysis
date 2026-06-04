"""Generate the reproducible IPL summary-analysis notebook.

The committed repository contains match, batting, and bowling summary CSVs.
This notebook intentionally uses only those files so it can run from a fresh
clone without the large raw Cricsheet ball-by-ball archive.
"""

from __future__ import annotations

from pathlib import Path

import nbformat as nbf


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_PATH = ROOT / "IPL_Evolution_Analysis.ipynb"


def code_cell(source: str):
    return nbf.v4.new_code_cell(source.strip())


def markdown_cell(source: str):
    return nbf.v4.new_markdown_cell(source.strip())


def build_notebook():
    nb = nbf.v4.new_notebook()
    nb.metadata = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {
            "name": "python",
            "version": "3.x",
        },
    }

    cells = [
        markdown_cell(
            """
# IPL Evolution Data Analysis

This notebook explores how IPL cricket changed from 2008 to 2025 using the
summary datasets committed in this repository:

- `data/ipl_matches.csv`
- `data/ipl_batting_stats.csv`
- `data/ipl_bowling_stats.csv`

The committed snapshot contains 1,169 match summaries through 2025-06-03.
See `data/DATASET.md` for source, coverage, transformations, and limitations.

The raw Cricsheet ball-by-ball archive is intentionally not committed because
it is large. The optional `scripts/process_data.py` pipeline can rebuild these
summary files when `data/ipl_raw/` is available locally.
            """
        ),
        code_cell(
            """
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_DIR = Path("data")
matches = pd.read_csv(DATA_DIR / "ipl_matches.csv", parse_dates=["date"])
batting = pd.read_csv(DATA_DIR / "ipl_batting_stats.csv")
bowling = pd.read_csv(DATA_DIR / "ipl_bowling_stats.csv")

for frame in (matches, batting, bowling):
    frame["season"] = frame["season"].astype(str)

matches["season_int"] = matches["season"].astype(int)
batting["season_int"] = batting["season"].astype(int)
bowling["season_int"] = bowling["season"].astype(int)

print("Dataset summary")
print(f"Matches: {len(matches):,}")
print(f"Seasons: {matches['season'].min()}-{matches['season'].max()} ({matches['season'].nunique()} seasons)")
print(f"Batting season-player rows: {len(batting):,}")
print(f"Bowling season-player rows: {len(bowling):,}")
            """
        ),
        markdown_cell(
            """
## 1. Scoring Has Accelerated

The first question is whether IPL scoring has increased over time. Match-level
data is enough to compare average match totals, run rate, and boundary volume
by season.
            """
        ),
        code_cell(
            """
season_scoring = (
    matches.groupby(["season", "season_int"], as_index=False)
    .agg(
        matches=("match_id", "count"),
        avg_total_runs=("total_runs", "mean"),
        avg_run_rate=("total_runs", lambda s: (s.sum() / matches.loc[s.index, "total_balls"].sum()) * 6),
        avg_balls_per_match=("total_balls", "mean"),
        fours_per_match=("total_fours", "mean"),
        sixes_per_match=("total_sixes", "mean"),
    )
    .sort_values("season_int")
)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_bar(
    x=season_scoring["season"],
    y=season_scoring["avg_total_runs"],
    name="Average match runs",
    marker_color="#10b981",
)
fig.add_scatter(
    x=season_scoring["season"],
    y=season_scoring["avg_run_rate"],
    name="Run rate",
    mode="lines+markers",
    line=dict(color="#f59e0b", width=3),
    secondary_y=True,
)
fig.update_layout(
    title="IPL scoring trend by season",
    template="plotly_dark",
    height=520,
    xaxis_title="Season",
)
fig.update_yaxes(title_text="Average match runs", secondary_y=False)
fig.update_yaxes(title_text="Runs per over", secondary_y=True)
fig.show()

season_scoring.tail(5)
            """
        ),
        markdown_cell(
            """
## 2. Boundary Hitting Changed the Shape of Scores

Boundary counts show whether the scoring rise is driven by strike rotation,
fours, or six-hitting.
            """
        ),
        code_cell(
            """
boundary = season_scoring.assign(
    fours_per_100_balls=lambda df: (df["fours_per_match"] / (df["avg_balls_per_match"] / 100)).round(2),
    sixes_per_100_balls=lambda df: (df["sixes_per_match"] / (df["avg_balls_per_match"] / 100)).round(2),
)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=boundary["season"],
    y=boundary["fours_per_match"],
    name="Fours per match",
    fill="tozeroy",
    line=dict(color="#06b6d4"),
))
fig.add_trace(go.Scatter(
    x=boundary["season"],
    y=boundary["sixes_per_match"],
    name="Sixes per match",
    fill="tozeroy",
    line=dict(color="#f59e0b"),
))
fig.update_layout(
    title="Boundary volume by season",
    template="plotly_dark",
    height=500,
    xaxis_title="Season",
    yaxis_title="Boundaries per match",
)
fig.show()
            """
        ),
        markdown_cell(
            """
## 3. Bowlers Adapted Under Pressure

The bowler summary data lets us compare seasonal economy and wicket-taking.
The important signal is not just that economy increased, but whether wickets
collapsed at the same time.
            """
        ),
        code_cell(
            """
bowling_trend = (
    bowling.replace([float("inf")], pd.NA)
    .groupby(["season", "season_int"], as_index=False)
    .agg(
        avg_economy=("economy", "mean"),
        total_wickets=("wickets", "sum"),
        avg_bowling_sr=("bowling_sr", "mean"),
    )
    .sort_values("season_int")
)

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_scatter(
    x=bowling_trend["season"],
    y=bowling_trend["avg_economy"],
    mode="lines+markers",
    name="Average economy",
    line=dict(color="#ef4444", width=3),
)
fig.add_bar(
    x=bowling_trend["season"],
    y=bowling_trend["total_wickets"],
    name="Total wickets",
    marker_color="#8b5cf6",
    opacity=0.65,
    secondary_y=True,
)
fig.update_layout(
    title="Bowling pressure across IPL seasons",
    template="plotly_dark",
    height=520,
    xaxis_title="Season",
)
fig.update_yaxes(title_text="Economy", secondary_y=False)
fig.update_yaxes(title_text="Wickets", secondary_y=True)
fig.show()
            """
        ),
        markdown_cell(
            """
## 4. Toss Advantage Is Limited

The match summary file tracks toss winners and match winners, so we can test
whether toss wins translate into match wins.
            """
        ),
        code_cell(
            """
completed_matches = matches.dropna(subset=["winner"]).copy()
toss = completed_matches.assign(toss_won_match=completed_matches["toss_winner"] == completed_matches["winner"])
toss_trend = (
    toss.groupby(["season", "season_int"], as_index=False)
    .agg(
        toss_win_match_pct=("toss_won_match", "mean"),
        field_first_pct=("toss_decision", lambda s: (s == "field").mean()),
    )
    .sort_values("season_int")
)
toss_trend[["toss_win_match_pct", "field_first_pct"]] *= 100

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=toss_trend["season"],
    y=toss_trend["toss_win_match_pct"],
    mode="lines+markers",
    name="Toss winner also won match",
    line=dict(color="#10b981", width=3),
))
fig.add_trace(go.Scatter(
    x=toss_trend["season"],
    y=toss_trend["field_first_pct"],
    mode="lines+markers",
    name="Chose to field first",
    line=dict(color="#f59e0b", width=3),
))
fig.add_hline(y=50, line_dash="dash", line_color="#94a3b8")
fig.update_layout(
    title="Toss impact and chase preference",
    template="plotly_dark",
    height=520,
    xaxis_title="Season",
    yaxis_title="Percent",
)
fig.show()
            """
        ),
        markdown_cell(
            """
## 5. Player Leaderboards

The summary tables are also useful for portfolio-style leaderboards: aggregate
player seasons into career totals, then compare volume and efficiency.
            """
        ),
        code_cell(
            """
batters = (
    batting.groupby("striker", as_index=False)
    .agg(
        runs=("runs", "sum"),
        balls=("balls_faced", "sum"),
        fours=("fours", "sum"),
        sixes=("sixes", "sum"),
        dismissals=("dismissals", "sum"),
    )
)
batters["strike_rate"] = (batters["runs"] / batters["balls"] * 100).round(2)
batters["average"] = (batters["runs"] / batters["dismissals"].replace(0, pd.NA)).round(2)
top_batters = batters.sort_values("runs", ascending=False).head(15)

fig = px.bar(
    top_batters,
    x="runs",
    y="striker",
    color="strike_rate",
    orientation="h",
    title="Top IPL run scorers in the included dataset",
    template="plotly_dark",
    color_continuous_scale="Viridis",
)
fig.update_layout(height=620, yaxis={"categoryorder": "total ascending"})
fig.show()
            """
        ),
        code_cell(
            """
bowlers = (
    bowling.groupby("bowler", as_index=False)
    .agg(
        wickets=("wickets", "sum"),
        runs_conceded=("runs_conceded", "sum"),
        extras=("extras_conceded", "sum"),
        balls=("balls_bowled", "sum"),
    )
)
bowlers["economy"] = ((bowlers["runs_conceded"] + bowlers["extras"]) / (bowlers["balls"] / 6)).round(2)
top_bowlers = bowlers.sort_values("wickets", ascending=False).head(15)

fig = px.bar(
    top_bowlers,
    x="wickets",
    y="bowler",
    color="economy",
    orientation="h",
    title="Top IPL wicket takers in the included dataset",
    template="plotly_dark",
    color_continuous_scale="Turbo",
)
fig.update_layout(height=620, yaxis={"categoryorder": "total ascending"})
fig.show()
            """
        ),
        markdown_cell(
            """
## Conclusions

1. IPL scoring has moved upward across the sample, with late-era seasons showing
   higher match totals and run rates than the early years. The committed data
   shows an about 17% run-rate lift from 2008-2010 to 2023-2025.
2. Six-hitting is the clearest scoring shift: recent seasons show roughly 71.5%
   more sixes per match than the first three seasons.
3. Bowling economy rose, but wicket-taking remains a meaningful counterweight,
   suggesting adaptation rather than total bowler irrelevance.
4. Toss advantage is noisy and close to a coin flip when no-result matches are
   excluded; chase preference is often more visible than a true toss-win edge.

### Reproducibility Notes

- Run `python3 scripts/validate_data.py` before opening the notebook.
- Run `python3 scripts/summarize_findings.py` to reproduce the headline claims.
- Run `python3 scripts/summarize_findings.py --verify-readme` to check docs
  against the committed CSVs.
- Run `python3 scripts/create_notebook.py` to regenerate this notebook.
- Run `python3 scripts/process_data.py` only when the raw Cricsheet CSV archive
  is available under `data/ipl_raw/`.
            """
        ),
    ]

    nb.cells = cells
    return nb


def main() -> None:
    notebook = build_notebook()
    nbf.write(notebook, NOTEBOOK_PATH)
    print(f"Wrote {NOTEBOOK_PATH}")


if __name__ == "__main__":
    main()

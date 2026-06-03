"""Validate the committed IPL summary datasets."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

REQUIRED_COLUMNS = {
    "ipl_matches.csv": {
        "match_id",
        "season",
        "date",
        "total_runs",
        "total_balls",
        "total_fours",
        "total_sixes",
        "winner",
        "toss_winner",
        "toss_decision",
    },
    "ipl_batting_stats.csv": {
        "season",
        "striker",
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "dismissals",
        "strike_rate",
        "batting_avg",
    },
    "ipl_bowling_stats.csv": {
        "season",
        "bowler",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "extras_conceded",
        "economy",
    },
}


def validate_file(filename: str, required_columns: set[str]) -> pd.DataFrame:
    path = DATA_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Missing required data file: {path}")

    frame = pd.read_csv(path)
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        raise ValueError(f"{filename} is missing required columns: {missing}")
    if frame.empty:
        raise ValueError(f"{filename} is empty")
    if frame["season"].isna().any():
        raise ValueError(f"{filename} contains blank seasons")
    return frame


def main() -> None:
    frames = {
        filename: validate_file(filename, columns)
        for filename, columns in REQUIRED_COLUMNS.items()
    }

    matches = frames["ipl_matches.csv"]
    batting = frames["ipl_batting_stats.csv"]
    bowling = frames["ipl_bowling_stats.csv"]

    season_count = matches["season"].astype(str).nunique()
    if season_count < 10:
        raise ValueError(f"Expected at least 10 seasons, found {season_count}")
    if matches["match_id"].duplicated().any():
        raise ValueError("ipl_matches.csv contains duplicate match_id values")
    if (matches["total_runs"] <= 0).any():
        raise ValueError("ipl_matches.csv contains non-positive total_runs")
    if (batting["balls_faced"] < 0).any():
        raise ValueError("ipl_batting_stats.csv contains negative balls_faced")
    if (bowling["balls_bowled"] < 0).any():
        raise ValueError("ipl_bowling_stats.csv contains negative balls_bowled")

    print("IPL summary datasets validated")
    print(f"- matches: {len(matches):,}")
    print(f"- batting rows: {len(batting):,}")
    print(f"- bowling rows: {len(bowling):,}")
    print(f"- seasons: {matches['season'].min()}-{matches['season'].max()} ({season_count})")


if __name__ == "__main__":
    main()

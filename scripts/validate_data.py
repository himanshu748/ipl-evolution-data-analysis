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
        "batting_first_won",
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
        "boundary_pct",
    },
    "ipl_bowling_stats.csv": {
        "season",
        "bowler",
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "extras_conceded",
        "economy",
        "bowling_avg",
        "bowling_sr",
    },
}

EXPECTED_SEASONS = set(range(2008, 2026))

NON_NEGATIVE_COLUMNS = {
    "ipl_matches.csv": {
        "total_runs",
        "total_balls",
        "total_fours",
        "total_sixes",
        "total_wickets",
        "total_extras",
        "innings1_runs",
        "innings2_runs",
    },
    "ipl_batting_stats.csv": {
        "runs",
        "balls_faced",
        "fours",
        "sixes",
        "dismissals",
        "strike_rate",
        "batting_avg",
        "boundary_pct",
    },
    "ipl_bowling_stats.csv": {
        "runs_conceded",
        "balls_bowled",
        "wickets",
        "extras_conceded",
        "economy",
        "bowling_avg",
        "bowling_sr",
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
    frame["season"] = pd.to_numeric(frame["season"], errors="raise").astype(int)
    return frame


def validate_non_negative(filename: str, frame: pd.DataFrame) -> None:
    for column in sorted(NON_NEGATIVE_COLUMNS[filename]):
        values = pd.to_numeric(frame[column], errors="raise")
        if (values < 0).any():
            raise ValueError(f"{filename} contains negative {column}")


def validate_season_contract(frames: dict[str, pd.DataFrame]) -> None:
    for filename, frame in frames.items():
        seasons = set(frame["season"].unique())
        if seasons != EXPECTED_SEASONS:
            missing = sorted(EXPECTED_SEASONS - seasons)
            extra = sorted(seasons - EXPECTED_SEASONS)
            raise ValueError(
                f"{filename} season coverage mismatch; missing={missing}, extra={extra}"
            )


def validate_matches(matches: pd.DataFrame) -> None:
    if matches["match_id"].duplicated().any():
        raise ValueError("ipl_matches.csv contains duplicate match_id values")
    parsed_dates = pd.to_datetime(matches["date"], errors="coerce")
    if parsed_dates.isna().any():
        raise ValueError("ipl_matches.csv contains unparsable dates")
    if (parsed_dates.dt.year != matches["season"]).any():
        raise ValueError("ipl_matches.csv contains dates outside their season year")
    if (matches["total_runs"] <= 0).any():
        raise ValueError("ipl_matches.csv contains non-positive total_runs")
    if (matches["total_balls"] <= 0).any():
        raise ValueError("ipl_matches.csv contains non-positive total_balls")
    innings_runs = matches["innings1_runs"] + matches["innings2_runs"]
    if (innings_runs > matches["total_runs"]).any():
        raise ValueError("ipl_matches.csv contains innings runs greater than total_runs")
    innings_wickets = matches["innings1_wickets"] + matches["innings2_wickets"]
    if (innings_wickets > matches["total_wickets"]).any():
        raise ValueError(
            "ipl_matches.csv contains innings wickets greater than total_wickets"
        )
    boundary_runs = matches["total_fours"] * 4 + matches["total_sixes"] * 6
    if (boundary_runs > matches["total_runs"]).any():
        raise ValueError("ipl_matches.csv contains boundary runs greater than total_runs")

    toss_decisions = set(matches["toss_decision"].dropna().unique())
    if toss_decisions - {"bat", "field"}:
        raise ValueError(f"Unexpected toss decisions: {sorted(toss_decisions)}")

    validate_match_team_fields(matches)


def validate_match_team_fields(matches: pd.DataFrame) -> None:
    teams = matches[["team1", "team2"]]
    toss_valid = (matches["toss_winner"] == teams["team1"]) | (
        matches["toss_winner"] == teams["team2"]
    )
    if (~toss_valid).any():
        raise ValueError("ipl_matches.csv contains toss_winner outside team1/team2")

    completed = matches[matches["winner"].notna()].copy()
    winner_valid = (completed["winner"] == completed["team1"]) | (
        completed["winner"] == completed["team2"]
    )
    if (~winner_valid).any():
        raise ValueError("ipl_matches.csv contains winner outside team1/team2")

    batting_first_valid = (matches["batting_first_team"] == teams["team1"]) | (
        matches["batting_first_team"] == teams["team2"]
    )
    if (~batting_first_valid).any():
        raise ValueError("ipl_matches.csv contains batting_first_team outside team1/team2")

    expected_batting_first_won = completed["winner"] == completed["batting_first_team"]
    if (completed["batting_first_won"] != expected_batting_first_won).any():
        raise ValueError("ipl_matches.csv contains inconsistent batting_first_won values")


def validate_unique_player_seasons(
    frame: pd.DataFrame,
    filename: str,
    player_column: str,
) -> None:
    duplicated = frame.duplicated(subset=["season", player_column])
    if duplicated.any():
        examples = (
            frame.loc[duplicated, ["season", player_column]]
            .head(5)
            .to_dict("records")
        )
        raise ValueError(f"{filename} contains duplicate season/player rows: {examples}")


def validate_batting(batting: pd.DataFrame) -> None:
    validate_unique_player_seasons(batting, "ipl_batting_stats.csv", "striker")
    if (batting["balls_faced"] == 0).any():
        raise ValueError("ipl_batting_stats.csv contains zero balls_faced rows")
    expected_strike_rate = (batting["runs"] / batting["balls_faced"] * 100).round(2)
    max_delta = (batting["strike_rate"] - expected_strike_rate).abs().max()
    if max_delta > 0.01:
        raise ValueError("ipl_batting_stats.csv contains inconsistent strike_rate values")


def validate_bowling(bowling: pd.DataFrame) -> None:
    validate_unique_player_seasons(bowling, "ipl_bowling_stats.csv", "bowler")
    if (bowling["balls_bowled"] == 0).any():
        raise ValueError("ipl_bowling_stats.csv contains zero balls_bowled rows")
    expected_economy = (
        (bowling["runs_conceded"] + bowling["extras_conceded"])
        / (bowling["balls_bowled"] / 6)
    ).round(2)
    max_delta = (bowling["economy"] - expected_economy).abs().max()
    if max_delta > 0.01:
        raise ValueError("ipl_bowling_stats.csv contains inconsistent economy values")


def main() -> None:
    frames = {
        filename: validate_file(filename, columns)
        for filename, columns in REQUIRED_COLUMNS.items()
    }
    for filename, frame in frames.items():
        validate_non_negative(filename, frame)
    validate_season_contract(frames)

    matches = frames["ipl_matches.csv"]
    batting = frames["ipl_batting_stats.csv"]
    bowling = frames["ipl_bowling_stats.csv"]

    season_count = matches["season"].astype(str).nunique()
    if season_count < 10:
        raise ValueError(f"Expected at least 10 seasons, found {season_count}")
    validate_matches(matches)
    validate_batting(batting)
    validate_bowling(bowling)

    print("IPL summary datasets validated")
    print(f"- matches: {len(matches):,}")
    print(f"- batting rows: {len(batting):,}")
    print(f"- bowling rows: {len(bowling):,}")
    print(f"- seasons: {matches['season'].min()}-{matches['season'].max()} ({season_count})")


if __name__ == "__main__":
    main()

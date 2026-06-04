"""Print reproducible headline findings from the committed IPL summaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
EARLY_SEASONS = (2008, 2009, 2010)
RECENT_SEASONS = (2023, 2024, 2025)


def pct_change(new_value: float, old_value: float) -> float:
    return ((new_value / old_value) - 1) * 100


def run_rate(frame: pd.DataFrame) -> float:
    return (frame["total_runs"].sum() / frame["total_balls"].sum()) * 6


def top_totals(
    frame: pd.DataFrame,
    group_column: str,
    value_column: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    totals = (
        frame.groupby(group_column, as_index=False)[value_column]
        .sum()
        .sort_values(value_column, ascending=False)
        .head(limit)
    )
    return totals.rename(columns={group_column: "name", value_column: "value"}).to_dict(
        "records"
    )


def build_summary() -> dict[str, Any]:
    matches = pd.read_csv(DATA_DIR / "ipl_matches.csv", parse_dates=["date"])
    batting = pd.read_csv(DATA_DIR / "ipl_batting_stats.csv")
    bowling = pd.read_csv(DATA_DIR / "ipl_bowling_stats.csv")

    early = matches[matches["season"].isin(EARLY_SEASONS)]
    recent = matches[matches["season"].isin(RECENT_SEASONS)]
    completed_matches = matches.dropna(subset=["winner"])

    early_run_rate = run_rate(early)
    recent_run_rate = run_rate(recent)
    early_sixes = early["total_sixes"].mean()
    recent_sixes = recent["total_sixes"].mean()

    summary = {
        "dataset": {
            "matches": int(len(matches)),
            "seasons": f"{matches['season'].min()}-{matches['season'].max()}",
            "latest_match_date": matches["date"].max().strftime("%Y-%m-%d"),
            "batting_rows": int(len(batting)),
            "bowling_rows": int(len(bowling)),
        },
        "scoring": {
            "early_seasons": list(EARLY_SEASONS),
            "recent_seasons": list(RECENT_SEASONS),
            "early_run_rate": round(early_run_rate, 2),
            "recent_run_rate": round(recent_run_rate, 2),
            "run_rate_change_pct": round(pct_change(recent_run_rate, early_run_rate), 1),
            "early_sixes_per_match": round(early_sixes, 2),
            "recent_sixes_per_match": round(recent_sixes, 2),
            "sixes_per_match_change_pct": round(pct_change(recent_sixes, early_sixes), 1),
        },
        "toss": {
            "completed_matches": int(len(completed_matches)),
            "toss_winner_match_win_pct": round(
                (completed_matches["toss_winner"] == completed_matches["winner"]).mean()
                * 100,
                1,
            ),
            "field_first_pct": round(
                (matches["toss_decision"] == "field").mean() * 100,
                1,
            ),
        },
        "leaders": {
            "top_run_scorers": top_totals(batting, "striker", "runs"),
            "top_wicket_takers": top_totals(bowling, "bowler", "wickets"),
        },
    }
    return summary


def format_pct(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".")


def verify_readme_claims(summary: dict[str, Any]) -> list[str]:
    readme = (ROOT / "README.md").read_text()
    dataset = summary["dataset"]
    scoring = summary["scoring"]
    expectations = {
        "match count": f"{dataset['matches']:,} IPL matches",
        "season coverage": f"{dataset['seasons']}",
        "latest match date": f"latest committed match date is {dataset['latest_match_date']}",
        "run-rate lift": f"about {format_pct(scoring['run_rate_change_pct'])}%",
        "sixes lift": f"about {format_pct(scoring['sixes_per_match_change_pct'])}%",
    }
    return [
        f"README missing {label}: {expected!r}"
        for label, expected in expectations.items()
        if expected not in readme
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize committed IPL analysis findings")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    parser.add_argument(
        "--verify-readme",
        action="store_true",
        help="Fail if README headline claims drift from committed CSVs",
    )
    args = parser.parse_args()

    summary = build_summary()
    if args.verify_readme:
        errors = verify_readme_claims(summary)
        if errors:
            raise SystemExit("\n".join(errors))
        print("README headline claims match committed data")
        return

    if args.json:
        print(json.dumps(summary, indent=2))
        return

    dataset = summary["dataset"]
    scoring = summary["scoring"]
    toss = summary["toss"]
    print("IPL findings summary")
    print(f"- matches: {dataset['matches']:,} across {dataset['seasons']}")
    print(f"- latest committed match date: {dataset['latest_match_date']}")
    print(
        "- run rate: "
        f"{scoring['early_run_rate']} ({min(EARLY_SEASONS)}-{max(EARLY_SEASONS)}) "
        f"to {scoring['recent_run_rate']} ({min(RECENT_SEASONS)}-{max(RECENT_SEASONS)}), "
        f"+{scoring['run_rate_change_pct']}%"
    )
    print(
        "- sixes per match: "
        f"{scoring['early_sixes_per_match']} to {scoring['recent_sixes_per_match']}, "
        f"+{scoring['sixes_per_match_change_pct']}%"
    )
    print(
        "- toss winner match-win rate: "
        f"{toss['toss_winner_match_win_pct']}% across completed matches"
    )
    print("- top run scorer:", summary["leaders"]["top_run_scorers"][0]["name"])
    print("- top wicket taker:", summary["leaders"]["top_wicket_takers"][0]["name"])


if __name__ == "__main__":
    main()

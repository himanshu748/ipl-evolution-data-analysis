import unittest

import pandas as pd

from scripts.validate_data import validate_matches, validate_unique_player_seasons


class ValidateDataTest(unittest.TestCase):
    def test_rejects_duplicate_batting_player_seasons(self):
        frame = pd.DataFrame(
            [
                {"season": 2025, "striker": "A Batter"},
                {"season": 2025, "striker": "A Batter"},
            ]
        )

        with self.assertRaisesRegex(ValueError, "duplicate season/player rows"):
            validate_unique_player_seasons(frame, "ipl_batting_stats.csv", "striker")

    def test_allows_same_player_across_different_seasons(self):
        frame = pd.DataFrame(
            [
                {"season": 2024, "bowler": "A Bowler"},
                {"season": 2025, "bowler": "A Bowler"},
            ]
        )

        validate_unique_player_seasons(frame, "ipl_bowling_stats.csv", "bowler")

    def test_validate_matches_rejects_boundary_runs_above_total(self):
        frame = valid_match_frame()
        frame.loc[0, "total_sixes"] = 40

        with self.assertRaisesRegex(ValueError, "boundary runs"):
            validate_matches(frame)

    def test_validate_matches_rejects_invalid_toss_winner(self):
        frame = valid_match_frame()
        frame.loc[0, "toss_winner"] = "Neutral XI"

        with self.assertRaisesRegex(ValueError, "toss_winner"):
            validate_matches(frame)

    def test_validate_matches_rejects_inconsistent_batting_first_won(self):
        frame = valid_match_frame()
        frame.loc[0, "batting_first_won"] = False

        with self.assertRaisesRegex(ValueError, "batting_first_won"):
            validate_matches(frame)

    def test_validate_matches_accepts_blank_winner_for_no_result(self):
        frame = valid_match_frame()
        frame.loc[0, "winner"] = pd.NA
        frame.loc[0, "batting_first_won"] = False

        validate_matches(frame)


def valid_match_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "match_id": 1,
                "season": 2025,
                "date": "2025-05-01",
                "team1": "Team A",
                "team2": "Team B",
                "toss_winner": "Team A",
                "toss_decision": "field",
                "winner": "Team A",
                "total_runs": 320,
                "total_balls": 240,
                "total_fours": 30,
                "total_sixes": 10,
                "total_wickets": 12,
                "innings1_runs": 150,
                "innings2_runs": 150,
                "innings1_wickets": 5,
                "innings2_wickets": 5,
                "batting_first_team": "Team A",
                "batting_first_won": True,
            }
        ]
    )


if __name__ == "__main__":
    unittest.main()

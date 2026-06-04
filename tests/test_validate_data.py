import unittest

import pandas as pd

from scripts.validate_data import validate_unique_player_seasons


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


if __name__ == "__main__":
    unittest.main()

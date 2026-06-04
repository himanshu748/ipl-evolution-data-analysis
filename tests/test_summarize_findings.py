import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import summarize_findings


class SummarizeFindingsTest(unittest.TestCase):
    def test_verify_docs_checks_dataset_card_coverage(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "data").mkdir()
            (root / "README.md").write_text(
                "1,169 IPL matches; 2008-2025; latest committed match date is "
                "2025-06-03; about 17%; about 71.5%"
            )
            (root / "data" / "DATASET.md").write_text(
                "\n".join(
                    [
                        "- Seasons: 2008-2025",
                        "- Match summaries: 1,169",
                        "- Batting rows: 2,783",
                        "- Bowling rows: 2,078",
                        "- Latest committed match date: 2025-06-03",
                        "- The committed CSVs are a static snapshot, not a live IPL feed.",
                    ]
                )
            )

            with patch.object(summarize_findings, "ROOT", root):
                self.assertEqual(summarize_findings.verify_docs(fake_summary()), [])

    def test_verify_docs_rejects_stale_dataset_card(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "data").mkdir()
            (root / "README.md").write_text(
                "1,169 IPL matches; 2008-2025; latest committed match date is "
                "2025-06-03; about 17%; about 71.5%"
            )
            (root / "data" / "DATASET.md").write_text(
                "- Seasons: 2008-2024\n"
                "- Match summaries: 1,100\n"
                "- The committed CSVs are a static snapshot."
            )

            with patch.object(summarize_findings, "ROOT", root):
                errors = summarize_findings.verify_docs(fake_summary())

            self.assertIn("data/DATASET.md missing season coverage", errors[0])
            self.assertGreaterEqual(len(errors), 4)


def fake_summary():
    return {
        "dataset": {
            "matches": 1169,
            "seasons": "2008-2025",
            "latest_match_date": "2025-06-03",
            "batting_rows": 2783,
            "bowling_rows": 2078,
        },
        "scoring": {
            "run_rate_change_pct": 17.0,
            "sixes_per_match_change_pct": 71.5,
        },
    }


if __name__ == "__main__":
    unittest.main()

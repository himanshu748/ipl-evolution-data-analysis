import unittest

from scripts.create_notebook import build_notebook


class CreateNotebookTest(unittest.TestCase):
    def test_generated_notebook_uses_stable_cell_ids(self):
        first = build_notebook()
        second = build_notebook()

        self.assertEqual(
            [cell["id"] for cell in first.cells],
            [cell["id"] for cell in second.cells],
        )
        self.assertEqual(first.cells[0]["id"], "ipl-evolution-01")


if __name__ == "__main__":
    unittest.main()

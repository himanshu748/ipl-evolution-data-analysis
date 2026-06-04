# IPL Summary Dataset Card

## Source

- Source: Cricsheet IPL ball-by-ball CSV archive
- Source website: https://cricsheet.org/
- Committed format: derived match summaries plus player-season batting and bowling summaries
- Raw archive status: not committed; place it under `data/ipl_raw/` to rebuild locally

## Coverage

- Seasons: 2008-2025
- Match summaries: 1,169
- Batting rows: 2,783 player-season rows
- Bowling rows: 2,078 player-season rows
- Latest committed match date: 2025-06-03

## Transformations

- `scripts/process_data.py` normalizes split-season labels and selected franchise rebrands.
- Match summaries aggregate runs, wickets, boundaries, innings totals, toss fields, and outcome fields.
- Batting summaries aggregate player-season runs, legal balls faced, boundaries, dismissals, strike rate, average, and boundary share.
- Bowling summaries aggregate player-season runs conceded, legal balls bowled, bowler-credited wickets, extras, economy, average, and strike rate.
- Player-season summary files are expected to contain one row per `(season, player)` grain.

## Limitations

- The committed CSVs are a static 2008-2025 snapshot, not a live IPL feed.
- 2026 and later IPL matches are intentionally excluded until the raw archive is refreshed and the summaries are regenerated.
- Player names and match metadata follow Cricsheet naming conventions after the limited normalizations in `scripts/process_data.py`.
- The notebook uses the committed summary CSVs only; it does not need the raw archive.

## Reproducibility

```bash
python3 scripts/validate_data.py
python3 scripts/summarize_findings.py
python3 scripts/summarize_findings.py --verify-readme
python3 -m unittest discover -s tests
python3 scripts/create_notebook.py
```

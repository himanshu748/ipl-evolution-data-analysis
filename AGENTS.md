# Repository Instructions

## Scope
This is a data-analysis repository built around committed IPL summary CSVs and a generated Jupyter notebook.

## Commands
- `python3 scripts/validate_data.py`
- `python3 scripts/summarize_findings.py --verify-readme`
- `python3 scripts/create_notebook.py`
- `PYTHONPYCACHEPREFIX=/private/tmp/ipl-pycache python3 -m compileall scripts`

## Conventions
- Keep the committed notebook runnable from the checked-in CSVs only.
- Do not commit large raw Cricsheet archives, generated cache files, exported chart dumps, or local notebook checkpoints.
- Treat `scripts/process_data.py` as an optional raw-data rebuild path that requires `data/ipl_raw/`.
- Keep `data/DATASET.md` aligned with committed CSV coverage and limitations.
- If the notebook changes, update `scripts/create_notebook.py` first and regenerate the notebook from the script.

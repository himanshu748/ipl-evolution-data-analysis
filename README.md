# The Evolution of Indian Cricket: How IPL Transformed a Nation's Game

### Codedex February 2026 Dataset Challenge Submission

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-6.x-3F4F75?style=for-the-badge&logo=plotly)](https://plotly.com)

---

## 📖 The Story

The **Indian Premier League (IPL)** launched in 2008 and fundamentally changed cricket forever. But beyond the fireworks and celebrity owners, **what does the data actually tell us?**

This project analyzes committed IPL summary datasets across **1,169 IPL matches** spanning **18 seasons (2008-2025)** to answer three key questions:

> 🔍 **Q1:** How has batting evolved? Are teams scoring faster than ever?  
> 🔍 **Q2:** Has the bat-vs-ball balance shifted? Are bowlers endangered?  
> 🔍 **Q3:** Is the toss advantage a myth or reality?

## 🎯 Key Findings

| # | Finding | Evidence |
|---|---------|----------|
| 1 | **The Run Explosion is Real** | Run rate rose about 17% from 2008-2010 to 2023-2025, with sixes per match up about 71% |
| 2 | **Bowlers Have Adapted, Not Died** | Despite soaring economy rates, wickets per match remain stable |
| 3 | **The Toss is (Mostly) Irrelevant** | Toss winner match-win rate is near 50% across completed matches, though chasing has become preferred in recent seasons |

### Surprise "Aha" Moment
> IPL scoring did not rise evenly. Six-hitting growth and high-scoring recent seasons changed the shape of match totals, while wickets remained a meaningful counterweight for bowlers.

## 📊 Visualizations

The notebook contains reproducible Plotly visualizations based only on the CSVs committed in this repository:

1. **The Run Explosion** - average match runs and run rate trend
2. **The Boundary Revolution** - fours and sixes per match
3. **Bowling Under Pressure** - economy and wicket-taking trends
4. **The Great Toss Debate** - toss-win conversion and field-first preference
5. **All-Time Run Scorers** - top batters colored by strike rate
6. **Top Wicket Takers** - top bowlers colored by economy

## 📂 Project Structure

```
ipl-evolution-data-analysis/
├── IPL_Evolution_Analysis.ipynb    # 📓 Main analysis notebook (submission)
├── README.md                       # 📋 This file
├── data/
│   ├── ipl_matches.csv             # 📊 1,169 match summaries
│   ├── ipl_batting_stats.csv       # 🏏 Player batting stats by season
│   └── ipl_bowling_stats.csv       # 🎳 Player bowling stats by season
├── scripts/
│   ├── validate_data.py            # ✅ Validate committed CSVs
│   ├── summarize_findings.py       # 📌 Recompute README headline claims
│   ├── process_data.py             # 🔧 Optional raw data -> clean datasets pipeline
│   └── create_notebook.py          # 📓 Notebook generator script
```

## 🛠️ How to Run

### Prerequisites
```bash
pip install pandas numpy plotly matplotlib seaborn jupyter
```

### Step 1: Validate the committed data
```bash
python3 scripts/validate_data.py
python3 scripts/summarize_findings.py
```

### Step 2: Regenerate the notebook
```bash
python3 scripts/create_notebook.py
```

### Step 3: Open the notebook
```bash
jupyter notebook IPL_Evolution_Analysis.ipynb
```

### Optional: Rebuild summary datasets from raw Cricsheet files

`scripts/process_data.py` expects the large raw IPL Cricsheet CSV archive under `data/ipl_raw/`. That raw archive is intentionally not committed. When available locally:

```bash
python3 scripts/process_data.py
python3 scripts/validate_data.py
python3 scripts/create_notebook.py
```

## 📋 Data Source

- **Source:** [Cricsheet.org](https://cricsheet.org/) — Open-source ball-by-ball cricket data
- **Committed Format:** CSV summary files for matches, batting-by-season, and bowling-by-season
- **Processing:** Optional raw match CSVs can be parsed into structured datasets using Python/Pandas
- **Current committed data:** 1,169 match summaries plus player-season batting and bowling summaries

## 🏅 Challenge Categories Targeted

| Category | How |
|----------|-----|
| 🏆 **Best Storyteller** | Full end-to-end narrative with clear questions, analysis, and conclusions |
| 😍 **Best Data Visualization** | Six focused interactive Plotly charts with a premium dark theme |
| 💡 **Sherlock "Aha" Moment** | Scoring growth + six-hitting pressure + toss myth |
| 💌 **Best Original Dataset** | Summary datasets processed from open Cricsheet data |

---

## Reproducibility Contract

- `scripts/validate_data.py` checks schema, exact 2008-2025 season coverage,
  non-negative metrics, date/season consistency, and recomputed strike
  rate/economy values.
- `scripts/summarize_findings.py` recomputes the README headline numbers from
  committed CSVs only, including toss calculations that exclude no-result
  matches.
- `scripts/create_notebook.py` is the source of truth for
  `IPL_Evolution_Analysis.ipynb`; update the script first, then regenerate.

---

*Made with ❤️ and 🏏 for the Codedex February 2026 Dataset Challenge*

# 🏏 The Evolution of Indian Cricket: How IPL Transformed a Nation's Game

### Codedex February 2026 Dataset Challenge Submission

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.x-150458?style=for-the-badge&logo=pandas)](https://pandas.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-6.x-3F4F75?style=for-the-badge&logo=plotly)](https://plotly.com)

---

## 📖 The Story

The **Indian Premier League (IPL)** launched in 2008 and fundamentally changed cricket forever. But beyond the fireworks and celebrity owners, **what does the data actually tell us?**

This project analyzes **278,205 ball-by-ball deliveries** across **1,169 IPL matches** spanning **17 seasons (2008–2025)** to answer three key questions:

> 🔍 **Q1:** How has batting evolved? Are teams scoring faster than ever?  
> 🔍 **Q2:** Has the bat-vs-ball balance shifted? Are bowlers endangered?  
> 🔍 **Q3:** Is the toss advantage a myth or reality?

## 🎯 Key Findings

| # | Finding | Evidence |
|---|---------|----------|
| 1 | **The Run Explosion is Real** | Average run rates have surged 25%+ since 2008, driven by a near-doubling of six-hitting frequency |
| 2 | **Bowlers Have Adapted, Not Died** | Despite soaring economy rates, wickets per match remain stable |
| 3 | **The Toss is (Mostly) Irrelevant** | Toss advantage hovers around 50%, though chasing has become preferred in recent seasons |

### 💡 Surprise "Aha" Moment
> **Death overs (16-20) run rates have exploded from ~8.5 RPO to 11+ RPO** — the last 5 overs have genuinely become a different game, driven by the rise of finishers like MS Dhoni, Hardik Pandya, and Rinku Singh.

## 📊 Visualizations

The notebook contains **10 interactive Plotly visualizations**:

1. 📈 **The Run Explosion** — Avg runs per match & run rate trend (dual-axis)
2. 💥 **The Boundary Revolution** — Fours vs Sixes per 100 balls (area chart)
3. 🎳 **The Bowlers Plight** — Economy rates vs Wickets per match (subplot)
4. 👑 **All-Time Run Scorers** — Top 15 batters colored by strike rate
5. 🪙 **The Great Toss Debate** — Toss win % & Chase vs Bat-first analysis
6. 🏆 **Franchise Dominance Map** — Team wins heatmap across seasons
7. 🏟️ **Run-Scoring Grounds** — Venue comparison with six-hitting data
8. 🌟 **Mr. Dependable** — Most Player of the Match awards
9. ⚡ **Three Phases of T20** — Powerplay vs Middle vs Death over scoring
10. 🎬 **Animated Evolution** — Strike rate vs Average scatter (play button!)

## 📂 Project Structure

```
feb_challenge/
├── IPL_Evolution_Analysis.ipynb    # 📓 Main analysis notebook (submission)
├── README.md                       # 📋 This file
├── data/
│   ├── ipl_raw/                    # 📦 Raw Cricsheet match files (1,169 × 2)
│   ├── ipl_deliveries.csv          # 🏏 278,205 ball-by-ball records
│   ├── ipl_matches.csv             # 📊 1,169 match summaries
│   ├── ipl_batting_stats.csv       # 🏏 Player batting stats by season
│   └── ipl_bowling_stats.csv       # 🎳 Player bowling stats by season
├── scripts/
│   ├── process_data.py             # 🔧 Raw data → clean datasets pipeline
│   └── create_notebook.py          # 📓 Notebook generator script
└── visuals/                        # 📸 Exported chart images
```

## 🛠️ How to Run

### Prerequisites
```bash
pip install pandas numpy plotly matplotlib seaborn jupyter
```

### Step 1: Process the data
```bash
python scripts/process_data.py
```

### Step 2: Open the notebook
```bash
jupyter notebook IPL_Evolution_Analysis.ipynb
```

## 📋 Data Source

- **Source:** [Cricsheet.org](https://cricsheet.org/) — Open-source ball-by-ball cricket data
- **Format:** CSV (ball-by-ball + match info files)
- **Processing:** Raw match CSVs (2,338 files) parsed and combined into 4 structured datasets using Python/Pandas
- **Total Data Points:** 278,205 deliveries across 1,169 matches

## 🏅 Challenge Categories Targeted

| Category | How |
|----------|-----|
| 🏆 **Best Storyteller** | Full end-to-end narrative with clear questions, analysis, and conclusions |
| 😍 **Best Data Visualization** | 10 interactive Plotly charts with premium dark theme |
| 💡 **Sherlock "Aha" Moment** | Death overs revolution insight + Six-hitting explosion |
| 💌 **Best Original Dataset** | Processed 2,338 raw Cricsheet files into clean datasets |

---

*Made with ❤️ and 🏏 for the Codedex February 2026 Dataset Challenge*

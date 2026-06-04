"""Build IPL summary CSVs from a local Cricsheet ball-by-ball archive."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "ipl_raw"
OUT_DIR = ROOT / "data"

BOWLER_CREDITED_WICKET_TYPES = {
    "bowled",
    "caught",
    "caught and bowled",
    "hit wicket",
    "lbw",
    "stumped",
}


def parse_info_file(filepath):
    """Parse a Cricsheet info CSV into a dictionary of match metadata."""
    info = {
        'teams': [],
        'players': {},
        'umpires': [],
    }
    with open(filepath, newline="") as f:
        for parts in csv.reader(f):
            if len(parts) < 2:
                continue
            if parts[0] == 'info':
                key = parts[1]
                if key == 'team':
                    info['teams'].append(parts[2])
                elif key == 'player':
                    team = parts[2]
                    player = parts[3] if len(parts) > 3 else ''
                    if team not in info['players']:
                        info['players'][team] = []
                    info['players'][team].append(player)
                elif key == 'umpire':
                    info['umpires'].append(parts[2])
                elif key in ('date', 'season', 'venue', 'city', 'toss_winner',
                             'toss_decision', 'player_of_match', 'winner',
                             'winner_runs', 'winner_wickets', 'method',
                             'outcome', 'eliminator', 'event', 'match_number'):
                    info[key] = parts[2] if len(parts) > 2 else ''
    return info


def delivery_flag(frame: pd.DataFrame, column: str) -> pd.Series:
    """Return a boolean flag for an optional Cricsheet extras column."""
    if column not in frame.columns:
        return pd.Series(False, index=frame.index)
    return frame[column].notna()


def legal_delivery_mask(frame: pd.DataFrame) -> pd.Series:
    """Cricket balls exclude wides and no-balls from bowler/batter ball counts."""
    return ~(delivery_flag(frame, "wides") | delivery_flag(frame, "noballs"))


def process_all_matches():
    """Process all match files and create consolidated DataFrames."""
    if not RAW_DIR.is_dir():
        raise FileNotFoundError(
            f"Raw Cricsheet directory not found: {RAW_DIR}. "
            "Download/extract the raw IPL CSV archive into data/ipl_raw/ "
            "or use scripts/validate_data.py with the committed summary CSVs."
        )

    files = [path.name for path in RAW_DIR.iterdir()]
    data_files = sorted([f for f in files if f.endswith('.csv') and '_info' not in f])
    info_files = sorted([f for f in files if f.endswith('_info.csv')])
    if not data_files or not info_files:
        raise FileNotFoundError(
            f"Expected match CSV and *_info.csv files in {RAW_DIR}; "
            f"found {len(data_files)} match files and {len(info_files)} info files."
        )

    print(f"Found {len(data_files)} match data files and {len(info_files)} info files")

    # Build a mapping from match_id to info
    info_map = {}
    for inf in info_files:
        match_id = inf.replace('_info.csv', '')
        try:
            info_map[match_id] = parse_info_file(RAW_DIR / inf)
        except Exception as e:
            print(f"  Skipping info file {inf}: {e}")

    # Read all ball-by-ball data
    all_dfs = []
    for i, df_file in enumerate(data_files):
        try:
            df = pd.read_csv(RAW_DIR / df_file, low_memory=False)
            all_dfs.append(df)
        except Exception as e:
            print(f"  Skipping match file {df_file}: {e}")
        if (i + 1) % 200 == 0:
            print(f"  Processed {i + 1}/{len(data_files)} files...")

    print(f"Combining {len(all_dfs)} DataFrames...")
    if not all_dfs:
        raise ValueError("No match data files could be parsed")
    balls_df = pd.concat(all_dfs, ignore_index=True)
    print(f"Total deliveries: {len(balls_df):,}")
    for optional_extra in ("wides", "noballs"):
        if optional_extra not in balls_df.columns:
            balls_df[optional_extra] = pd.NA

    # CRITICAL: Normalize season to string to avoid mixed int/str duplicates
    balls_df['season'] = balls_df['season'].astype(str)

    # Normalize split-season names to single years
    season_norm = {
        '2007/08': '2008', '2009/10': '2010', '2020/21': '2020'
    }
    balls_df['season'] = balls_df['season'].replace(season_norm)
    print(f"Unique seasons after normalization: {sorted(balls_df['season'].unique())}")

    # Normalize team names (franchise rebrandings)
    team_norm = {
        'Royal Challengers Bengaluru': 'Royal Challengers Bangalore',
        'Delhi Capitals': 'Delhi Daredevils',
        'Punjab Kings': 'Kings XI Punjab',
        'Rising Pune Supergiants': 'Rising Pune Supergiant',
    }
    for col in ['batting_team', 'bowling_team']:
        if col in balls_df.columns:
            balls_df[col] = balls_df[col].replace(team_norm)

    # Parse dates
    balls_df['start_date'] = pd.to_datetime(balls_df['start_date'], errors='coerce')
    balls_df['year'] = balls_df['start_date'].dt.year

    # Create match-level summary
    print("Creating match summaries...")
    matches = []
    for match_id in balls_df['match_id'].unique():
        match_balls = balls_df[balls_df['match_id'] == match_id]
        mid = str(match_id)
        info = info_map.get(mid, {})

        season = match_balls['season'].iloc[0] if 'season' in match_balls.columns else info.get('season', '')
        date = match_balls['start_date'].iloc[0]
        venue = match_balls['venue'].iloc[0] if 'venue' in match_balls.columns else info.get('venue', '')

        teams = info.get('teams', list(match_balls['batting_team'].unique()[:2]))
        team1 = teams[0] if len(teams) > 0 else ''
        team2 = teams[1] if len(teams) > 1 else ''

        total_runs = match_balls['runs_off_bat'].sum() + match_balls['extras'].sum()
        total_wickets = match_balls['wicket_type'].notna().sum()
        total_fours = (match_balls['runs_off_bat'] == 4).sum()
        total_sixes = (match_balls['runs_off_bat'] == 6).sum()
        total_balls = int(legal_delivery_mask(match_balls).sum())
        total_extras = match_balls['extras'].sum()

        # Innings breakdown
        inn1 = match_balls[match_balls['innings'] == 1]
        inn2 = match_balls[match_balls['innings'] == 2]

        inn1_runs = inn1['runs_off_bat'].sum() + inn1['extras'].sum()
        inn2_runs = inn2['runs_off_bat'].sum() + inn2['extras'].sum()
        inn1_wickets = inn1['wicket_type'].notna().sum()
        inn2_wickets = inn2['wicket_type'].notna().sum()

        matches.append({
            'match_id': match_id,
            'season': season,
            'date': date,
            'venue': venue,
            'city': info.get('city', ''),
            'team1': team1,
            'team2': team2,
            'toss_winner': info.get('toss_winner', ''),
            'toss_decision': info.get('toss_decision', ''),
            'winner': info.get('winner', ''),
            'winner_runs': info.get('winner_runs', ''),
            'winner_wickets': info.get('winner_wickets', ''),
            'player_of_match': info.get('player_of_match', ''),
            'total_runs': total_runs,
            'total_wickets': total_wickets,
            'total_fours': total_fours,
            'total_sixes': total_sixes,
            'total_balls': total_balls,
            'total_extras': total_extras,
            'innings1_runs': inn1_runs,
            'innings2_runs': inn2_runs,
            'innings1_wickets': inn1_wickets,
            'innings2_wickets': inn2_wickets,
            'batting_first_team': inn1['batting_team'].iloc[0] if len(inn1) > 0 else '',
            'batting_second_team': inn2['batting_team'].iloc[0] if len(inn2) > 0 else '',
        })

    matches_df = pd.DataFrame(matches)
    matches_df['date'] = pd.to_datetime(matches_df['date'], errors='coerce')

    # Normalize team names in match-level data
    for col in ['team1', 'team2', 'winner', 'toss_winner', 'batting_first_team', 'batting_second_team']:
        matches_df[col] = matches_df[col].replace(team_norm)

    # Determine if batting first won
    matches_df['batting_first_won'] = matches_df['winner'] == matches_df['batting_first_team']

    print(f"Total matches: {len(matches_df)}")
    matches_df['season'] = matches_df['season'].astype(str)
    print(f"Seasons: {sorted(matches_df['season'].unique())}")

    # Create player-level batting stats per season
    print("Creating player batting stats...")
    legal_batting_balls = balls_df[legal_delivery_mask(balls_df)]
    batting_balls = (
        legal_batting_balls.groupby(['season', 'striker'])
        .size()
        .reset_index(name='balls_faced')
    )
    batting_stats = balls_df.groupby(['season', 'striker']).agg(
        runs=('runs_off_bat', 'sum'),
        fours=('runs_off_bat', lambda x: (x == 4).sum()),
        sixes=('runs_off_bat', lambda x: (x == 6).sum()),
    ).reset_index()
    batting_stats = batting_stats.merge(batting_balls, on=['season', 'striker'], how='left')
    batting_stats['balls_faced'] = batting_stats['balls_faced'].fillna(0).astype(int)

    # Simpler dismissals calc
    dismissals = balls_df[balls_df['player_dismissed'].notna()].groupby(
        ['season', 'player_dismissed']
    ).size().reset_index(name='dismissals')
    dismissals.rename(columns={'player_dismissed': 'striker'}, inplace=True)

    batting_stats = batting_stats.merge(dismissals, on=['season', 'striker'], how='left')
    batting_stats['dismissals'] = batting_stats['dismissals'].fillna(0).astype(int)
    batting_stats = batting_stats[batting_stats['balls_faced'] > 0].copy()
    batting_stats['strike_rate'] = (batting_stats['runs'] / batting_stats['balls_faced'] * 100).round(2)
    batting_stats['batting_avg'] = batting_stats.apply(
        lambda r: r['runs'] / r['dismissals'] if r['dismissals'] > 0 else r['runs'], axis=1
    ).round(2)
    batting_stats['boundary_pct'] = (
        (batting_stats['fours'] * 4 + batting_stats['sixes'] * 6) / batting_stats['runs'].replace(0, 1) * 100
    ).round(2)

    # Create player-level bowling stats per season
    print("Creating player bowling stats...")
    bowling_balls = (
        balls_df[legal_delivery_mask(balls_df)]
        .groupby(['season', 'bowler'])
        .size()
        .reset_index(name='balls_bowled')
    )
    bowler_wickets = (
        balls_df[balls_df['wicket_type'].isin(BOWLER_CREDITED_WICKET_TYPES)]
        .groupby(['season', 'bowler'])
        .size()
        .reset_index(name='wickets')
    )

    bowling_stats = balls_df.groupby(['season', 'bowler']).agg(
        runs_conceded=('runs_off_bat', 'sum'),
        extras_conceded=('extras', 'sum'),
        wides=('wides', lambda x: x.notna().sum()),
        noballs=('noballs', lambda x: x.notna().sum()),
    ).reset_index()
    bowling_stats = bowling_stats.merge(bowling_balls, on=['season', 'bowler'], how='left')
    bowling_stats = bowling_stats.merge(bowler_wickets, on=['season', 'bowler'], how='left')
    bowling_stats['balls_bowled'] = bowling_stats['balls_bowled'].fillna(0).astype(int)
    bowling_stats['wickets'] = bowling_stats['wickets'].fillna(0).astype(int)
    bowling_stats = bowling_stats[bowling_stats['balls_bowled'] > 0].copy()

    bowling_stats['economy'] = (
        (bowling_stats['runs_conceded'] + bowling_stats['extras_conceded']) /
        (bowling_stats['balls_bowled'] / 6)
    ).round(2)
    bowling_stats['bowling_avg'] = bowling_stats.apply(
        lambda r: (r['runs_conceded'] + r['extras_conceded']) / r['wickets']
        if r['wickets'] > 0 else float('inf'), axis=1
    ).round(2)
    bowling_stats['bowling_sr'] = bowling_stats.apply(
        lambda r: r['balls_bowled'] / r['wickets'] if r['wickets'] > 0 else float('inf'), axis=1
    ).round(2)

    # Save all datasets
    print("Saving processed datasets...")
    balls_df.to_csv(OUT_DIR / 'ipl_deliveries.csv', index=False)
    matches_df.to_csv(OUT_DIR / 'ipl_matches.csv', index=False)
    batting_stats.to_csv(OUT_DIR / 'ipl_batting_stats.csv', index=False)
    bowling_stats.to_csv(OUT_DIR / 'ipl_bowling_stats.csv', index=False)

    print("\n✅ Data processing complete!")
    print(f"  - ipl_deliveries.csv: {len(balls_df):,} rows")
    print(f"  - ipl_matches.csv: {len(matches_df):,} rows")
    print(f"  - ipl_batting_stats.csv: {len(batting_stats):,} rows")
    print(f"  - ipl_bowling_stats.csv: {len(bowling_stats):,} rows")

    return balls_df, matches_df, batting_stats, bowling_stats


if __name__ == '__main__':
    process_all_matches()

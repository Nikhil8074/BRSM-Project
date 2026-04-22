import pandas as pd
import numpy as np
from scipy import stats
import os
import glob
import re

DATA_DIR = './BRSM data csv/BRSM data csv'
DEMO_PATH = './BRSM data csv/Demographic data.xlsx'
OUT_DIR = './plots'
EXCLUDE_LIST = ['sub42_NB', 'sub151_NB', 'sub36_AB', 'sub161_NB', 'sub32_AB']

def load_participant_data():
    """Load all valid participant CSV files and return as a list of dictionaries."""
    all_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
    records = []
    
    # Load movie durations
    abrupt_movies = pd.read_csv('./BRSM data csv/abruptmovies.csv')
    natural_movies = pd.read_csv('./BRSM data csv/naturalmovies.csv')
    
    # Extract movie_id from path/metadata if not already explicit
    # movie_id in participant files usually starts from 1
    # We can create a mapping for movie_id -> duration
    # Since movie_id is 1-indexed and corresponds to the order in the csv
    ab_durations = {i+1: row['duration'] for i, row in abrupt_movies.iterrows()}
    nb_durations = {i+1: row['duration'] for i, row in natural_movies.iterrows()}
    
    for file in all_files:
        filename = os.path.basename(file)
        match = re.search(r'sub(\d+)_(NB|AB)', filename)
        if not match:
            continue
            
        sub_num = int(match.group(1))
        condition = match.group(2)
        sub_id = f"sub{sub_num}_{condition}"
        
        if sub_num <= 13 or sub_id in EXCLUDE_LIST:
            continue
            
        try:
            df = pd.read_csv(file, low_memory=False)
            
            corr_col = 'recogloop.resp.corr' if 'recogloop.resp.corr' in df.columns else 'resp.corr'
            rt_col = 'recogloop.resp.rt' if 'recogloop.resp.rt' in df.columns else 'resp.rt'
            conf_col = 'recogloop.conf_radio.response' if 'recogloop.conf_radio.response' in df.columns else 'conf_radio.response'
            
            trials = df.dropna(subset=[corr_col]).copy()
            
            def clean_numeric(val):
                if isinstance(val, str):
                    val = val.strip('[]').split(',')[0]
                return pd.to_numeric(val, errors='coerce')

            trials[corr_col] = trials[corr_col].apply(clean_numeric)
            trials[rt_col] = trials[rt_col].apply(clean_numeric)
            
            if conf_col in trials.columns:
                trials[conf_col] = trials[conf_col].apply(clean_numeric)
                
            if 'target_img' in df.columns:
                trials['FrameType'] = trials['target_img'].astype(str).apply(
                    lambda x: 'BB' if 'BB' in x.upper() else ('EM' if 'EM' in x.upper() else 'Unknown'))
            
            # Map duration
            dur_map = ab_durations if condition == 'AB' else nb_durations
            if 'movie_id' in trials.columns:
                trials['Duration'] = trials['movie_id'].map(dur_map)
            
            records.append({
                'sub_id': sub_id, 
                'sub_num': sub_num, 
                'condition': condition, 
                'trials': trials,
                'corr_col': corr_col,
                'rt_col': rt_col,
                'conf_col': conf_col
            })
        except Exception as e:
            print(f"  Error loading {filename}: {e}")
            
    print(f"Loaded {len(records)} valid participant files.")
    return records

def run_ttest(group1, group2, label, tail='two-sided'):
    g1 = group1.dropna()
    g2 = group2.dropna()
    
    t_stat, p_two = stats.ttest_ind(g1, g2, equal_var=False)
    
    if tail == 'greater':
        p = p_two / 2 if t_stat > 0 else 1 - p_two / 2
        tail_label = 'one-tailed (greater)'
    elif tail == 'less':
        p = p_two / 2 if t_stat < 0 else 1 - p_two / 2
        tail_label = 'one-tailed (less)'
    else:
        p = p_two
        tail_label = 'two-tailed'
        
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    
    print(f"  {label}")
    print(f"    n1={len(g1)}, n2={len(g2)}, M1={g1.mean():.4f}, M2={g2.mean():.4f}")
    print(f"    t = {t_stat:.4f}, p ({tail_label}) = {p:.4f}  {sig}")
    
    return {
        'label': label, 
        'n1': len(g1), 'n2': len(g2),
        'M1': g1.mean(), 'SD1': g1.std(), 
        'M2': g2.mean(), 'SD2': g2.std(),
        't': t_stat, 'p': p, 
        'tail': tail_label, 'sig': sig
    }

def save_results(results, filename):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, filename)
    pd.DataFrame(results).to_csv(path, index=False)
    print(f"  -> Saved results to: {filename}\n")

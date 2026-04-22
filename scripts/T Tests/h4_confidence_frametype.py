import pandas as pd
import numpy as np
import analytical_utils as utils

def run_analysis():
    print("=" * 60)
    print("HYPOTHESIS 4: Confidence Calibration Across Frame Types")
    print("=" * 60)
    
    records = utils.load_participant_data()
    h4_rows = []
    
    for r in records:
        t = r['trials']
        cf = r['conf_col']
        if 'FrameType' not in t.columns:
            continue
            
        valid = t[t[cf].between(1, 5, inclusive='both')].copy()
        
        for ft in ['BB', 'EM']:
            sub = valid[valid['FrameType'] == ft]
            conf_mean = sub[cf].mean()
            h4_rows.append({'condition': r['condition'], 'FrameType': ft, 'Confidence': conf_mean})
    
    h4_df = pd.DataFrame(h4_rows)
    
    results = []
    for ft, label in [('BB', 'Before Boundary'), ('EM', 'Event Middle')]:
        nb = h4_df[(h4_df.condition == 'NB') & (h4_df.FrameType == ft)]['Confidence']
        ab = h4_df[(h4_df.condition == 'AB') & (h4_df.FrameType == ft)]['Confidence']
        
        tail = 'greater' if ft == 'BB' else 'two-sided'
        results.append(utils.run_ttest(nb, ab, f"Confidence ({label}): NB vs AB", tail=tail))
    
    utils.save_results(results, 'h4_ttest_results.csv')

if __name__ == "__main__":
    run_analysis()

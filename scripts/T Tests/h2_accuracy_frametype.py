import pandas as pd
import numpy as np
import analytical_utils as utils

def run_analysis():
    print("=" * 60)
    print("HYPOTHESIS 2: Accuracy Across Frame Types")
    print("=" * 60)
    
    records = utils.load_participant_data()
    h2_rows = []
    
    for r in records:
        t = r['trials']
        if 'FrameType' not in t.columns:
            continue
            
        for ft in ['BB', 'EM']:
            sub = t[t['FrameType'] == ft]
            acc = sub[r['corr_col']].mean()
            h2_rows.append({'condition': r['condition'], 'FrameType': ft, 'Accuracy': acc})
    
    h2_df = pd.DataFrame(h2_rows)
    
    results = []
    for ft, label in [('BB', 'Before Boundary'), ('EM', 'Event Middle')]:
        nb = h2_df[(h2_df.condition == 'NB') & (h2_df.FrameType == ft)]['Accuracy']
        ab = h2_df[(h2_df.condition == 'AB') & (h2_df.FrameType == ft)]['Accuracy']
        
        tail = 'greater' if ft == 'BB' else 'two-sided'
        results.append(utils.run_ttest(nb, ab, f"Accuracy ({label}): NB vs AB", tail=tail))
    
    utils.save_results(results, 'h2_ttest_results.csv')

if __name__ == "__main__":
    run_analysis()

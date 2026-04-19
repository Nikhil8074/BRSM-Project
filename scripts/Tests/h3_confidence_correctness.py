import pandas as pd
import numpy as np
import analytical_utils as utils

def run_analysis():
    print("=" * 60)
    print("HYPOTHESIS 3: Confidence and Correctness")
    print("=" * 60)
    
    records = utils.load_participant_data()
    h3_rows = []
    
    for r in records:
        t = r['trials']
        cf, cr = r['conf_col'], r['corr_col']
        
        valid = t[t[cf].between(1, 5, inclusive='both')].copy()
        
        for correctness in [1, 0]:
            sub = valid[valid[cr] == correctness]
            conf_mean = sub[cf].mean()
            label = 'Correct' if correctness == 1 else 'Incorrect'
            h3_rows.append({'condition': r['condition'], 'Correctness': label, 'Confidence': conf_mean})
    
    h3_df = pd.DataFrame(h3_rows)
    
    results = []
    for corr_label, tail in [('Correct', 'greater'), ('Incorrect', 'two-sided')]:
        nb = h3_df[(h3_df.condition == 'NB') & (h3_df.Correctness == corr_label)]['Confidence']
        ab = h3_df[(h3_df.condition == 'AB') & (h3_df.Correctness == corr_label)]['Confidence']
        results.append(utils.run_ttest(nb, ab, f"Confidence ({corr_label} Responses): NB vs AB", tail=tail))
    
    utils.save_results(results, 'h3_ttest_results.csv')

if __name__ == "__main__":
    run_analysis()

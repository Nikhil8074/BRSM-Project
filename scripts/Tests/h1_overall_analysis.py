import pandas as pd
import numpy as np
import analytical_utils as utils

def run_analysis():
    print("=" * 60)
    print("HYPOTHESIS 1: Overall Accuracy & Response Time")
    print("=" * 60)
    
    records = utils.load_participant_data()
    h1_rows = []
    
    for r in records:
        t = r['trials']
        acc = t[r['corr_col']].mean()
        rt = t[r['rt_col']].dropna().mean()
        h1_rows.append({'condition': r['condition'], 'Accuracy': acc, 'RT': rt})
    
    h1_df = pd.DataFrame(h1_rows)
    
    nb_acc = h1_df[h1_df.condition == 'NB']['Accuracy']
    ab_acc = h1_df[h1_df.condition == 'AB']['Accuracy']
    nb_rt = h1_df[h1_df.condition == 'NB']['RT']
    ab_rt = h1_df[h1_df.condition == 'AB']['RT']
    
    results = []
    results.append(utils.run_ttest(nb_acc, ab_acc, "Overall Accuracy: NB > AB", tail='greater'))
    results.append(utils.run_ttest(nb_rt, ab_rt, "Overall Response Time: NB < AB", tail='less'))
    
    utils.save_results(results, 'h1_ttest_results.csv')

if __name__ == "__main__":
    run_analysis()

import pandas as pd
import numpy as np
from scipy import stats
import analytical_utils as utils
import re
import os

def run_analysis():
    records = utils.load_participant_data()
    h5_acc = []
    for r in records:
        acc = r['trials'][r['corr_col']].mean()
        h5_acc.append({'SubNum': r['sub_num'], 'Accuracy': acc})
    h5_acc_df = pd.DataFrame(h5_acc)
    
    demo_df = pd.read_excel(utils.DEMO_PATH)
    demo_df.columns = [str(c).strip() for c in demo_df.columns]
    
    def extract_num(x):
        m = re.search(r'sub(\d+)', str(x))
        return int(m.group(1)) if m else None
    
    demo_df['SubNum'] = demo_df['Sub ID'].apply(extract_num)
    demo_df = demo_df.dropna(subset=['SubNum'])
    demo_df['SubNum'] = demo_df['SubNum'].astype(int)
    
    valid_subs = h5_acc_df['SubNum'].tolist()
    merged = h5_acc_df.merge(demo_df, on='SubNum', how='inner')
    
    merged['Gender'] = merged['Gender '].astype(str).str.strip().str.capitalize() if 'Gender ' in merged.columns else merged['Gender'].astype(str).str.strip().str.capitalize()
    merged['Handedness'] = merged['Handedness'].astype(str).str.strip().str.capitalize()
    merged['Vision'] = merged['Vision'].astype(str).str.strip().str.capitalize()
    
    results = []
    
    male_acc = merged[merged['Gender'] == 'Male']['Accuracy']
    female_acc = merged[merged['Gender'] == 'Female']['Accuracy']
    results.append(utils.run_ttest(male_acc, female_acc, "Accuracy: Male vs Female", tail='two-sided'))
    
    right_acc = merged[merged['Handedness'].str.contains('Right', na=False)]['Accuracy']
    left_acc = merged[merged['Handedness'].str.contains('Left', na=False)]['Accuracy']
    results.append(utils.run_ttest(right_acc, left_acc, "Accuracy: Right-Handed vs Left-Handed", tail='two-sided'))
    
    normal_acc = merged[merged['Vision'] == 'Normal']['Accuracy']
    corrected_acc = merged[merged['Vision'].str.contains('Corrected', na=False)]['Accuracy']
    results.append(utils.run_ttest(normal_acc, corrected_acc, "Accuracy: Normal vs Corrected Vision", tail='two-sided'))
    
    age_acc_data = merged[['Age', 'Accuracy']].dropna()
    r_val, p_val = stats.pearsonr(age_acc_data['Age'], age_acc_data['Accuracy'])
    sig = '***' if p_val < 0.001 else ('**' if p_val < 0.01 else ('*' if p_val < 0.05 else 'ns'))
    print(f"  Accuracy ~ Age Correlation:")
    print(f"    n={len(age_acc_data)}, r={r_val:.4f}, p={p_val:.4f}  {sig}")
    
    results.append({
        'label': 'Accuracy ~ Age (Pearson Correlation)',
        'n1': len(age_acc_data), 'n2': np.nan,
        'M1': age_acc_data['Age'].mean(), 'SD1': age_acc_data['Age'].std(),
        'M2': age_acc_data['Accuracy'].mean(), 'SD2': age_acc_data['Accuracy'].std(),
        't': r_val,
        'p': p_val, 'tail': 'Correlation', 'sig': sig
    })
    
    utils.save_results(results, 'h5_ttest_results.csv')

if __name__ == "__main__":
    run_analysis()

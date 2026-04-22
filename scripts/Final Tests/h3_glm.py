import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from analytical_utils import load_participant_data

def cohens_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)

def run_analysis():
    print("\n--- [H3] Confidence Interaction (Condition * Correctness) ---")
    
    # 1. Load Data
    records = load_participant_data()
    all_trials = []
    
    for r in records:
        df = r['trials'].copy()
        df['Condition'] = r['condition']
        df['IsCorrect'] = df[r['corr_col']].astype(float)
        df['Confidence'] = df[r['conf_col']]
        all_trials.append(df)
        
    df_trials = pd.concat(all_trials, ignore_index=True)
    
    # 2. GLM Analysis
    model = smf.ols('Confidence ~ C(Condition, Treatment("NB")) * C(IsCorrect, Treatment(1.0))', data=df_trials).fit()
    print(model.summary().tables[1])
    
    # Cohen's d for Condition (Correct Responses)
    conf_nb_corr = df_trials[(df_trials['Condition'] == 'NB') & (df_trials['IsCorrect'] == 1.0)]['Confidence']
    conf_ab_corr = df_trials[(df_trials['Condition'] == 'AB') & (df_trials['IsCorrect'] == 1.0)]['Confidence']
    print(f"  Effect Size (Cohen's d - Correct): {cohens_d(conf_nb_corr, conf_ab_corr):.3f}")
    
    # Simple Effects
    print("  Simple Effects (Condition for Correct vs Incorrect):")
    for corr in [1.0, 0.0]:
        subset = df_trials[df_trials['IsCorrect'] == corr]
        m = smf.ols('Confidence ~ C(Condition, Treatment("NB"))', data=subset).fit()
        p = m.pvalues['C(Condition, Treatment("NB"))[T.AB]']
        label = "Correct" if corr == 1.0 else "Incorrect"
        print(f"    {label}: Natural vs Abrupt p={p:.4f}")

if __name__ == "__main__":
    run_analysis()

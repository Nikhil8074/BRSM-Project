import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from analytical_utils import load_participant_data

def run_analysis():
    print("\n--- [H2] Accuracy Interaction (Condition * FrameType) ---")
    
    # 1. Load Data
    records = load_participant_data()
    all_trials = []
    
    for r in records:
        df = r['trials'].copy()
        df['Condition'] = r['condition']
        df['Accuracy'] = df[r['corr_col']]
        all_trials.append(df)
        
    df_trials = pd.concat(all_trials, ignore_index=True)
    df_trials['IsCorrect'] = df_trials['Accuracy'].astype(float)
    
    # 2. GLM Analysis
    model = smf.logit('IsCorrect ~ C(Condition, Treatment("NB")) * C(FrameType, Treatment("EM"))', data=df_trials).fit(disp=0)
    print(model.summary().tables[1])
    
    # Odds Ratio for Condition
    or_cond = np.exp(model.params['C(Condition, Treatment("NB"))[T.AB]'])
    print(f"  Condition Odds Ratio (AB vs NB): {or_cond:.3f}")
    
    # Simple Effects
    print("  Simple Effects (Condition for each FrameType):")
    for ft in ['BB', 'EM']:
        subset = df_trials[df_trials['FrameType'] == ft]
        m = smf.logit('Accuracy ~ C(Condition, Treatment("NB"))', data=subset).fit(disp=0)
        p = m.pvalues['C(Condition, Treatment("NB"))[T.AB]']
        print(f"    {ft}: Natural vs Abrupt p={p:.4f}")

if __name__ == "__main__":
    run_analysis()

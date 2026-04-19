import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from analytical_utils import load_participant_data
import os

def cohens_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)

# Create output directory for results
OUT_DIR = './Plots,Stats,Test Results'
os.makedirs(OUT_DIR, exist_ok=True)

def run_analysis():
    print("--- Movie Memory Experiment: Final Statistical Analysis ---")
    
    # 1. Load Data
    records = load_participant_data()
    all_trials = []
    participant_summary = []
    
    for r in records:
        df = r['trials'].copy()
        df['Condition'] = r['condition']
        df['SubID'] = r['sub_id']
        
        # Standardize columns
        df['Accuracy'] = df[r['corr_col']]
        df['RT'] = df[r['rt_col']]
        df['Confidence'] = df[r['conf_col']]
        
        all_trials.append(df)
        
        # Participant averages for non-parametric tests
        participant_summary.append({
            'SubID': r['sub_id'],
            'Condition': r['condition'],
            'Accuracy': df['Accuracy'].mean(),
            'RT': df['RT'].mean(),
            'Confidence': df['Confidence'].mean()
        })
        
    df_trials = pd.concat(all_trials, ignore_index=True)
    df_participants = pd.DataFrame(participant_summary)
    
    print(f"Total Trials: {len(df_trials)}")
    print(f"Total Participants: {len(df_participants)}")

    # 2. Hypothesis 1: Overall Accuracy & RT (Mann-Whitney U)
    print("\n[H1] Overall Group Comparisons (Mann-Whitney U)")
    acc_nb = df_participants[df_participants['Condition'] == 'NB']['Accuracy']
    acc_ab = df_participants[df_participants['Condition'] == 'AB']['Accuracy']
    rt_nb = df_participants[df_participants['Condition'] == 'NB']['RT']
    rt_ab = df_participants[df_participants['Condition'] == 'AB']['RT']
    
    u_acc, p_acc = stats.mannwhitneyu(acc_nb, acc_ab, alternative='two-sided')
    u_rt, p_rt = stats.mannwhitneyu(rt_nb, rt_ab, alternative='two-sided')
    print(f"  Accuracy: U={u_acc:.2f}, p={p_acc:.4f}")
    print(f"    Effect Size (Cohen's d): {cohens_d(acc_nb, acc_ab):.3f}")
    print(f"  RT: U={u_rt:.2f}, p={p_rt:.4f}")
    print(f"    Effect Size (Cohen's d): {cohens_d(rt_nb, rt_ab):.3f}")

    # 3. Hypothesis 2: Accuracy (Condition x FrameType)
    print("\n[H2] Accuracy Interaction (Condition * FrameType)")
    df_trials['IsCorrect'] = df_trials['Accuracy'].astype(float)
    model_h2 = smf.logit('IsCorrect ~ C(Condition, Treatment("NB")) * C(FrameType, Treatment("EM"))', data=df_trials).fit(disp=0)
    print(model_h2.summary().tables[1])
    
    # Odds Ratio for Condition
    or_cond = np.exp(model_h2.params['C(Condition, Treatment("NB"))[T.AB]'])
    print(f"  Condition Odds Ratio (AB vs NB): {or_cond:.3f}")
    
    # Simple Effects for H2
    print("  Simple Effects (Condition for each FrameType):")
    for ft in ['BB', 'EM']:
        subset = df_trials[df_trials['FrameType'] == ft]
        m = smf.logit('Accuracy ~ C(Condition, Treatment("NB"))', data=subset).fit(disp=0)
        p = m.pvalues['C(Condition, Treatment("NB"))[T.AB]']
        print(f"    {ft}: Natural vs Abrupt p={p:.4f}")

    # 4. Hypothesis 3: Confidence x Correctness
    print("\n[H3] Confidence Interaction (Condition * Correctness)")
    model_h3 = smf.ols('Confidence ~ C(Condition, Treatment("NB")) * C(IsCorrect, Treatment(1.0))', data=df_trials).fit()
    print(model_h3.summary().tables[1])
    
    # Cohen's d for Condition (Correct Responses)
    conf_nb_corr = df_trials[(df_trials['Condition'] == 'NB') & (df_trials['IsCorrect'] == 1.0)]['Confidence']
    conf_ab_corr = df_trials[(df_trials['Condition'] == 'AB') & (df_trials['IsCorrect'] == 1.0)]['Confidence']
    print(f"  Effect Size (Cohen's d - Correct): {cohens_d(conf_nb_corr, conf_ab_corr):.3f}")
    
    # Simple Effects for H3
    print("  Simple Effects (Condition for Correct vs Incorrect):")
    for corr in [1.0, 0.0]:
        subset = df_trials[df_trials['IsCorrect'] == corr]
        m = smf.ols('Confidence ~ C(Condition, Treatment("NB"))', data=subset).fit()
        p = m.pvalues['C(Condition, Treatment("NB"))[T.AB]']
        label = "Correct" if corr == 1.0 else "Incorrect"
        print(f"    {label}: Natural vs Abrupt p={p:.4f}")

    # 5. Hypothesis 4: Confidence x FrameType
    print("\n[H4] Confidence Interaction (Condition * FrameType)")
    model_h4 = smf.ols('Confidence ~ C(Condition, Treatment("NB")) * C(FrameType, Treatment("EM"))', data=df_trials).fit()
    print(model_h4.summary().tables[1])
    
    # Cohen's d for Condition (Before Boundary)
    conf_nb_bb = df_trials[(df_trials['Condition'] == 'NB') & (df_trials['FrameType'] == 'BB')]['Confidence']
    conf_ab_bb = df_trials[(df_trials['Condition'] == 'AB') & (df_trials['FrameType'] == 'BB')]['Confidence']
    print(f"  Effect Size (Cohen's d - BB): {cohens_d(conf_nb_bb, conf_ab_bb):.3f}")
    
    # Simple Effects for H4
    print("  Simple Effects (Condition for each FrameType):")
    for ft in ['BB', 'EM']:
        subset = df_trials[df_trials['FrameType'] == ft]
        m = smf.ols('Confidence ~ C(Condition, Treatment("NB"))', data=subset).fit()
        p = m.pvalues['C(Condition, Treatment("NB"))[T.AB]']
        print(f"    {ft}: Natural vs Abrupt p={p:.4f}")

    # 6. Hypothesis 5: Demographics
    print("\n[H5] Demographic Effects (Multiple Regression)")
    # Use the imputed demographics CSV
    demo_df = pd.read_csv('./BRSM data csv/Imputed Demographics.csv')
    
    # Merge demographics with participant summary
    # Both now have Sub ID as primary key
    df_demo_merged = pd.merge(df_participants, demo_df, left_on='SubID', right_on='Sub ID', how='inner')
    
    # Standardize factors for regression
    df_demo_merged['Vision_Simple'] = df_demo_merged['Vision'].astype(str).str.lower().str.contains('corrected').map({True: 'Corrected', False: 'Normal'})
    df_demo_merged['Hand_Simple'] = df_demo_merged['Handedness'].astype(str).str.lower().apply(lambda x: 'right' if 'right' in x else 'left')
    df_demo_merged['Gender_Simple'] = df_demo_merged['Gender'].astype(str).str.lower()
    
    model_h5 = smf.ols('Accuracy ~ C(Condition, Treatment("NB")) + Age + C(Gender_Simple) + C(Hand_Simple) + C(Vision_Simple)', data=df_demo_merged).fit()
    print(model_h5.summary().tables[1])

if __name__ == "__main__":
    run_analysis()

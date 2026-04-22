import pandas as pd
import numpy as np
import scipy.stats as stats
from analytical_utils import load_participant_data

def cohens_d(x, y):
    nx, ny = len(x), len(y)
    dof = nx + ny - 2
    return (np.mean(x) - np.mean(y)) / np.sqrt(((nx-1)*np.std(x, ddof=1)**2 + (ny-1)*np.std(y, ddof=1)**2) / dof)

def run_analysis():
    print("\n--- [H1] Overall Group Comparisons (Mann-Whitney U) ---")
    
    # 1. Load Data
    records = load_participant_data()
    participant_summary = []
    
    for r in records:
        df = r['trials']
        participant_summary.append({
            'SubID': r['sub_id'],
            'Condition': r['condition'],
            'Accuracy': df[r['corr_col']].mean(),
            'RT': df[r['rt_col']].mean()
        })
        
    df_participants = pd.DataFrame(participant_summary)
    
    # 2. Analysis
    acc_nb = df_participants[df_participants['Condition'] == 'NB']['Accuracy']
    acc_ab = df_participants[df_participants['Condition'] == 'AB']['Accuracy']
    rt_nb = df_participants[df_participants['Condition'] == 'NB']['RT']
    rt_ab = df_participants[df_participants['Condition'] == 'AB']['RT']
    
    u_acc, p_acc = stats.mannwhitneyu(acc_nb, acc_ab, alternative='two-sided')
    u_rt, p_rt = stats.mannwhitneyu(rt_nb, rt_ab, alternative='two-sided')
    
    print(f"Total Participants: {len(df_participants)}")
    print(f"  Accuracy: U={u_acc:.2f}, p={p_acc:.4f}")
    print(f"    Effect Size (Cohen's d): {cohens_d(acc_nb, acc_ab):.3f}")
    print(f"  RT: U={u_rt:.2f}, p={p_rt:.4f}")
    print(f"    Effect Size (Cohen's d): {cohens_d(rt_nb, rt_ab):.3f}")

if __name__ == "__main__":
    run_analysis()

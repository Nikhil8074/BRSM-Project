import pandas as pd
import numpy as np
import analytical_utils as utils
from scipy import stats
import matplotlib.pyplot as plt
import os

# Explicitly set output directory to match project structure
RESULTS_DIR = '/home/nikhil.repala/BRSM/Project/Plots,Stats,Test Results'
PLOTS_DIR = os.path.join(RESULTS_DIR, 'normality_plots')
os.makedirs(PLOTS_DIR, exist_ok=True)

def perform_normality_analysis():
    print("=" * 60)
    print("NORMALITY TESTING (Shapiro-Wilk)")
    print("=" * 60)
    
    records = utils.load_participant_data()
    
    # 1. Prepare Data Containers
    data_map = {
        'NB': {'Accuracy': [], 'RT': [], 'Conf_Corr': [], 'Conf_Incorr': [], 'Acc_BB': [], 'Acc_EM': [], 'Conf_BB': [], 'Conf_EM': []},
        'AB': {'Accuracy': [], 'RT': [], 'Conf_Corr': [], 'Conf_Incorr': [], 'Acc_BB': [], 'Acc_EM': [], 'Conf_BB': [], 'Conf_EM': []}
    }
    
    for r in records:
        cond = r['condition']
        trials = r['trials']
        
        # Overall
        data_map[cond]['Accuracy'].append(trials[r['corr_col']].mean())
        data_map[cond]['RT'].append(trials[r['rt_col']].mean())
        
        # Frame Type split
        bb_trials = trials[trials['FrameType'] == 'BB']
        em_trials = trials[trials['FrameType'] == 'EM']
        
        if not bb_trials.empty:
            data_map[cond]['Acc_BB'].append(bb_trials[r['corr_col']].mean())
            if r['conf_col'] in bb_trials.columns:
                data_map[cond]['Conf_BB'].append(bb_trials[r['conf_col']].mean())
        
        if not em_trials.empty:
            data_map[cond]['Acc_EM'].append(em_trials[r['corr_col']].mean())
            if r['conf_col'] in em_trials.columns:
                data_map[cond]['Conf_EM'].append(em_trials[r['conf_col']].mean())
        
        # Correctness split (Confidence)
        if r['conf_col'] in trials.columns:
            corr_trials = trials[trials[r['corr_col']] == 1]
            incorr_trials = trials[trials[r['corr_col']] == 0]
            
            if not corr_trials.empty:
                data_map[cond]['Conf_Corr'].append(corr_trials[r['conf_col']].mean())
            if not incorr_trials.empty:
                data_map[cond]['Conf_Incorr'].append(incorr_trials[r['conf_col']].mean())

    results = []
    
    # 2. Run Tests and Plot
    for cond in ['NB', 'AB']:
        for var_name, values in data_map[cond].items():
            if len(values) < 3:
                continue
            
            data = np.array(values)
            # Remove NaNs
            data = data[~np.isnan(data)]
            
            if len(data) < 3:
                continue
                
            shapiro_stat, shapiro_p = stats.shapiro(data)
            sig = 'Violates Normality (p < 0.05)' if shapiro_p < 0.05 else 'Normally Distributed (p >= 0.05)'
            
            print(f"[{cond}] {var_name}: stat={shapiro_stat:.4f}, p={shapiro_p:.4f} -> {sig}")
            
            results.append({
                'Condition': cond,
                'Variable': var_name,
                'n': len(data),
                'Shapiro_Stat': shapiro_stat,
                'Shapiro_p': shapiro_p,
                'Assessment': sig
            })
            
            # Plotting
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Histogram
            ax1.hist(data, bins=15, color='skyblue', edgecolor='black', alpha=0.7)
            ax1.set_title(f'Histogram: {cond} {var_name}')
            ax1.set_xlabel('Value')
            ax1.set_ylabel('Frequency')
            
            # Q-Q Plot
            stats.probplot(data, dist="norm", plot=ax2)
            ax2.set_title(f'Q-Q Plot: {cond} {var_name}')
            
            plt.tight_layout()
            plot_filename = f'normality_{cond}_{var_name}.png'
            plt.savefig(os.path.join(PLOTS_DIR, plot_filename))
            plt.close()

    # 3. Save Stats
    res_df = pd.DataFrame(results)
    res_df.to_csv(os.path.join(RESULTS_DIR, 'normality_results.csv'), index=False)
    print(f"\nSaved normality results to: {os.path.join(RESULTS_DIR, 'normality_results.csv')}")
    print(f"Saved plots to: {PLOTS_DIR}")

if __name__ == "__main__":
    perform_normality_analysis()

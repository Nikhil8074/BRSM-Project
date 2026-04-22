import pandas as pd
import numpy as np
import scipy.stats as stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import seaborn as sns
from analytical_utils import load_participant_data
import os

# Output directory
OUT_DIR = './Plots_Stats_Test_Results/video_length'
os.makedirs(OUT_DIR, exist_ok=True)

def run_analysis():
    print("--- Video Length Hypothesis Analysis ---")
    
    # 1. Load Enriched Data
    records = load_participant_data()
    all_trials = []
    
    for r in records:
        df = r['trials'].copy()
        df['Condition'] = r['condition']
        df['SubID'] = r['sub_id']
        
        # Standardize columns
        df['Accuracy'] = df[r['corr_col']]
        df['RT'] = df[r['rt_col']]
        df['Confidence'] = df[r['conf_col']]
        
        all_trials.append(df)
        
    df_trials = pd.concat(all_trials, ignore_index=True)
    
    # Drop trials with missing durations or accuracy
    df_trials = df_trials.dropna(subset=['Duration', 'Accuracy', 'RT', 'Confidence'])
    
    # Aggregate data by Video (movie_id) and Condition
    # This helps us see the pattern across different videos
    video_summary = df_trials.groupby(['Duration', 'Condition', 'movie_id']).agg({
        'Accuracy': 'mean',
        'RT': 'mean',
        'Confidence': 'mean'
    }).reset_index()
    
    # 2. Visualizations
    sns.set_theme(style="whitegrid")
    palette = {"NB": "#4C72B0", "AB": "#C44E52"}
    
    # Accuracy vs Duration
    plt.figure(figsize=(10, 6))
    sns.regplot(data=video_summary[video_summary['Condition'] == 'NB'], x='Duration', y='Accuracy', 
                label='Natural (NB)', color=palette['NB'], scatter_kws={'alpha':0.5})
    sns.regplot(data=video_summary[video_summary['Condition'] == 'AB'], x='Duration', y='Accuracy', 
                label='Abrupt (AB)', color=palette['AB'], scatter_kws={'alpha':0.5})
    plt.title('Memory Accuracy vs. Video Duration', fontsize=14)
    plt.xlabel('Video Duration (seconds)', fontsize=12)
    plt.ylabel('Mean Accuracy', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'accuracy_vs_duration.png'), dpi=300)
    plt.close()
    
    # RT vs Duration
    plt.figure(figsize=(10, 6))
    sns.regplot(data=video_summary[video_summary['Condition'] == 'NB'], x='Duration', y='RT', 
                label='Natural (NB)', color=palette['NB'], scatter_kws={'alpha':0.5})
    sns.regplot(data=video_summary[video_summary['Condition'] == 'AB'], x='Duration', y='RT', 
                label='Abrupt (AB)', color=palette['AB'], scatter_kws={'alpha':0.5})
    plt.title('Response Time vs. Video Duration', fontsize=14)
    plt.xlabel('Video Duration (seconds)', fontsize=12)
    plt.ylabel('Mean Response Time (s)', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'rt_vs_duration.png'), dpi=300)
    plt.close()

    # Confidence vs Duration
    plt.figure(figsize=(10, 6))
    sns.regplot(data=video_summary[video_summary['Condition'] == 'NB'], x='Duration', y='Confidence', 
                label='Natural (NB)', color=palette['NB'], scatter_kws={'alpha':0.5})
    sns.regplot(data=video_summary[video_summary['Condition'] == 'AB'], x='Duration', y='Confidence', 
                label='Abrupt (AB)', color=palette['AB'], scatter_kws={'alpha':0.5})
    plt.title('Confidence vs. Video Duration', fontsize=14)
    plt.xlabel('Video Duration (seconds)', fontsize=12)
    plt.ylabel('Mean Confidence', fontsize=12)
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, 'confidence_vs_duration.png'), dpi=300)
    plt.close()

    # 3. Statistical Analysis
    print("\n[Statistical Tests: Interaction Analysis]")
    
    # Logistic regression for Accuracy (trial-level)
    # Testing for interaction between Condition and Duration
    # Accuracy ~ Condition * Duration
    model_acc = smf.logit('Accuracy ~ C(Condition, Treatment("NB")) * Duration', data=df_trials).fit(disp=0)
    print("\n--- Accuracy Interaction ---")
    print(model_acc.summary().tables[1])
    
    # Linear regression for RT
    model_rt = smf.ols('RT ~ C(Condition, Treatment("NB")) * Duration', data=df_trials).fit()
    print("\n--- Response Time Interaction ---")
    print(model_rt.summary().tables[1])
    
    # Linear regression for Confidence
    model_conf = smf.ols('Confidence ~ C(Condition, Treatment("NB")) * Duration', data=df_trials).fit()
    print("\n--- Confidence Interaction ---")
    print(model_conf.summary().tables[1])
    
    # Correlation coefficients
    print("\n[Correlations per Group]")
    for cond in ['NB', 'AB']:
        sub = video_summary[video_summary['Condition'] == cond]
        corr_acc, p_acc = stats.pearsonr(sub['Duration'], sub['Accuracy'])
        corr_rt, p_rt = stats.pearsonr(sub['Duration'], sub['RT'])
        print(f"  Condition: {cond}")
        print(f"    Duration-Accuracy: r={corr_acc:.3f}, p={p_acc:.4f}")
        print(f"    Duration-RT: r={corr_rt:.3f}, p={p_rt:.4f}")

    # 4. Descriptive Statistics
    print("\n[Descriptive Statistics]")
    desc_stats = df_trials.groupby('Condition').agg({
        'Accuracy': ['mean', 'std', 'count'],
        'RT': ['mean', 'std'],
        'Confidence': ['mean', 'std']
    }).round(3)
    print(desc_stats)

    # Save to separate file
    with open(os.path.join(OUT_DIR, 'descriptive_stats.txt'), 'w') as f:
        f.write("Descriptive Statistics for Video Length Analysis\n")
        f.write("================================================\n\n")
        f.write(desc_stats.to_string())
        f.write("\n\n(Values are aggregated at the trial level)\n")

    # Save summary to file
    with open(os.path.join(OUT_DIR, 'statistical_results.txt'), 'w') as f:
        f.write("Video Length Hypothesis Statistical Results\n")
        f.write("==========================================\n\n")
        f.write("Accuracy Interaction (Logit):\n")
        f.write(str(model_acc.summary().tables[1]))
        f.write("\n\nRT Interaction (OLS):\n")
        f.write(str(model_rt.summary().tables[1]))
        f.write("\n\nConfidence Interaction (OLS):\n")
        f.write(str(model_conf.summary().tables[1]))
        f.write("\n\nGroup Correlations:\n")
        for cond in ['NB', 'AB']:
            sub = video_summary[video_summary['Condition'] == cond]
            corr_acc, p_acc = stats.pearsonr(sub['Duration'], sub['Accuracy'])
            f.write(f"  {cond}: Dur-Acc r={corr_acc:.3f}, p={p_acc:.4f}\n")

if __name__ == "__main__":
    run_analysis()

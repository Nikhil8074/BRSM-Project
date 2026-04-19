import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
import re

data_dir = '/home/nikhil.repala/BRSM/Project/BRSM data csv/BRSM data csv'
all_files = glob.glob(os.path.join(data_dir, '*.csv'))

exclude_list = ['sub42_NB', 'sub151_NB', 'sub36_AB', 'sub161_NB', 'sub32_AB']

results = []

for file in all_files:
    filename = os.path.basename(file)
    match = re.search(r'sub(\d+)_(NB|AB)', filename)
    if not match:
        continue
    
    sub_num = int(match.group(1))
    condition = match.group(2)
    sub_id = f"sub{sub_num}_{condition}"
    
    if sub_num <= 13 or sub_id in exclude_list:
        continue
        
    try:
        df = pd.read_csv(file, low_memory=False)
        corr_col = 'recogloop.resp.corr' if 'recogloop.resp.corr' in df.columns else 'resp.corr'
        rt_col = 'recogloop.resp.rt' if 'recogloop.resp.rt' in df.columns else 'resp.rt'
        
        recog_trials = df.dropna(subset=[corr_col]).copy()
        
        if len(recog_trials) == 0:
            continue
            
        recog_trials[corr_col] = recog_trials[corr_col].astype(str).str.strip('[]').str.split(',').str[0]
        recog_trials[corr_col] = pd.to_numeric(recog_trials[corr_col], errors='coerce')
        
        recog_trials[rt_col] = recog_trials[rt_col].astype(str).str.strip('[]').str.split(',').str[0]
        recog_trials[rt_col] = pd.to_numeric(recog_trials[rt_col], errors='coerce')
        
        valid_rts = recog_trials[recog_trials[rt_col] > 0]
        
        acc = recog_trials[corr_col].mean()
        
        rt = valid_rts[rt_col].mean()
        
        results.append({
            'Subject': sub_id,
            'Condition': 'Natural Cut (NB)' if condition == 'NB' else 'Abrupt Cut (AB)',
            'Accuracy': acc,
            'ResponseTime': rt
        })
    except Exception as e:
        print(f"Error processing {filename}: {e}")

df_res = pd.DataFrame(results)

print(f"Processed {len(df_res)} valid participant files.")
print("Summary Statistics:")

def rich_stats(series):
    q25 = series.quantile(0.25)
    q75 = series.quantile(0.75)
    return pd.Series({
        'count': series.count(),
        'mean': series.mean(),
        'std': series.std(),
        'median': series.median(),
        'mode': series.mode().iloc[0] if not series.mode().empty else np.nan,
        'IQR': q75 - q25,
        'Q25': q25,
        'Q75': q75,
        'min': series.min(),
        'max': series.max()
    })

stats_df = df_res.groupby('Condition')[['Accuracy', 'ResponseTime']].apply(
    lambda grp: grp[['Accuracy', 'ResponseTime']].apply(rich_stats)
).unstack(level=1)
print(stats_df)

out_dir = '/home/nikhil.repala/BRSM/Project/plots'
os.makedirs(out_dir, exist_ok=True)
stats_path = os.path.join(out_dir, 'h1_descriptive_stats.csv')
stats_df.to_csv(stats_path)
print(f"Saved descriptive statistics to {stats_path}")

out_dir = '/home/nikhil.repala/BRSM/Project/Plots_Stats_Test_Results'
os.makedirs(out_dir, exist_ok=True)

plt.style.use('seaborn-v0_8-whitegrid')
fig1, ax1 = plt.subplots(figsize=(8, 6))
fig1.patch.set_facecolor('#ffffff')
ax1.set_facecolor('#f9f9f9')

palette = {'Natural Cut (NB)': '#4C72B0', 'Abrupt Cut (AB)': '#C44E52'}

# Accuracy Violin Plot
sns.violinplot(data=df_res, x='Condition', y='Accuracy', ax=ax1, palette=palette, inner='quartile', zorder=2)
sns.stripplot(data=df_res, x='Condition', y='Accuracy', ax=ax1, color='black', alpha=0.3, jitter=True, zorder=3)
ax1.set_title('Overall Recognition Accuracy (H1)', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('Participant Accuracy (Proportion Correct)', fontsize=14)
ax1.set_xlabel('')
ax1.set_ylim(0, 1.05)
ax1.tick_params(labelsize=12)

for spine in ax1.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

out_path1 = os.path.join(out_dir, 'h1_acc_boxplot.png') # Keeping original filename for report consistency
fig1.savefig(out_path1, dpi=300, bbox_inches='tight')
print(f"Saved Accuracy Violin Plot to {out_path1}")
plt.close(fig1)

# Response Time Violin Plot
fig2, ax2 = plt.subplots(figsize=(8, 6))
fig2.patch.set_facecolor('#ffffff')
ax2.set_facecolor('#f9f9f9')

sns.violinplot(data=df_res, x='Condition', y='ResponseTime', ax=ax2, palette=palette, inner='quartile', zorder=2)
sns.stripplot(data=df_res, x='Condition', y='ResponseTime', ax=ax2, color='black', alpha=0.3, jitter=True, zorder=3)
ax2.set_title('Overall Recognition Response Time (H1)', fontsize=16, fontweight='bold', pad=15)
ax2.set_ylabel('Participant Response Time (s)', fontsize=14)
ax2.set_xlabel('')
ax2.tick_params(labelsize=12)

for spine in ax2.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

out_path2 = os.path.join(out_dir, 'h1_rt_boxplot.png') # Keeping original filename for report consistency
fig2.savefig(out_path2, dpi=300, bbox_inches='tight')
print(f"Saved Response Time Violin Plot to {out_path2}")
plt.close(fig2)

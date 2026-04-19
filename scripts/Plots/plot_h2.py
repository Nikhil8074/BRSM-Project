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
        
        if 'target_img' not in df.columns:
            continue
            
        recog_trials = df.dropna(subset=[corr_col, 'target_img']).copy()
        
        if len(recog_trials) == 0:
            continue
            
        recog_trials[corr_col] = recog_trials[corr_col].astype(str).str.strip('[]').str.split(',').str[0]
        recog_trials[corr_col] = pd.to_numeric(recog_trials[corr_col], errors='coerce')
        
        recog_trials['FrameType'] = recog_trials['target_img'].astype(str).apply(
            lambda x: 'Before Boundary (BB)' if 'BB' in x.upper() else ('Event Middle (EM)' if 'EM' in x.upper() else 'Unknown')
        )
        
        for frame_type in ['Before Boundary (BB)', 'Event Middle (EM)']:
            subset = recog_trials[recog_trials['FrameType'] == frame_type]
            if len(subset) > 0:
                acc = subset[corr_col].mean()
                results.append({
                    'Subject': sub_id,
                    'Condition': 'Natural Cut (NB)' if condition == 'NB' else 'Abrupt Cut (AB)',
                    'FrameType': frame_type,
                    'Accuracy': acc
                })
                
    except Exception as e:
        print(f"Error processing {filename}: {e}")

df_res = pd.DataFrame(results)

print(f"Processed valid participant files for H2.")

print("Summary Statistics (Hypothesis 2):")

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

stats_df = df_res.groupby(['Condition', 'FrameType'])['Accuracy'].apply(rich_stats).unstack()
print(stats_df)

out_dir = '/home/nikhil.repala/BRSM/Project/Plots_Stats_Test_Results'
os.makedirs(out_dir, exist_ok=True)
stats_path = os.path.join(out_dir, 'h2_descriptive_stats.csv')
stats_df.to_csv(stats_path)
print(f"Saved descriptive statistics to {stats_path}")

plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor('#ffffff')
ax.set_facecolor('#f9f9f9')

palette = {'Natural Cut (NB)': '#4C72B0', 'Abrupt Cut (AB)': '#C44E52'}

# Accuracy Violin Plot per Frame Type
sns.violinplot(data=df_res, x='FrameType', y='Accuracy', hue='Condition', ax=ax, palette=palette, inner='quartile', zorder=2, split=False)

sns.stripplot(data=df_res, x='FrameType', y='Accuracy', hue='Condition', ax=ax,
              color='black', alpha=0.3, jitter=True, dodge=True, zorder=3)
handles, labels = ax.get_legend_handles_labels()

ax.legend(handles[:2], labels[:2], title='Video Condition', fontsize=12, title_fontsize=13, loc='lower right')

ax.set_title('Recognition Accuracy Across Frame Types (H2)', fontsize=16, fontweight='bold', pad=15)
ax.set_ylabel('Participant Accuracy (Proportion Correct)', fontsize=14)
ax.set_xlabel('Frame Type', fontsize=14)
ax.set_ylim(0, 1.05)
ax.tick_params(labelsize=12)

for spine in ax.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

out_path = os.path.join(out_dir, 'h2_acc_frametype_boxplot.png') # Original name
fig.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Saved Hypothesis 2 Violin Plot to {out_path}")
plt.close(fig)

fig2, ax2 = plt.subplots(figsize=(8, 6))
fig2.patch.set_facecolor('#ffffff')
ax2.set_facecolor('#f9f9f9')

sns.pointplot(data=df_res, x='FrameType', y='Accuracy', hue='Condition', ax=ax2, 
              palette=palette, dodge=True, markers=['o', 's'], capsize=.1, errorbar=('ci', 95))

ax2.set_title('Accuracy Interaction: Frame Type x Condition (H2)', fontsize=16, fontweight='bold', pad=15)
ax2.set_ylabel('Mean Participant Accuracy (95% CI)', fontsize=14)
ax2.set_xlabel('Frame Type', fontsize=14)
ax2.set_ylim(0.75, 0.95) 
ax2.tick_params(labelsize=12)
ax2.legend(title='Video Condition', fontsize=12, title_fontsize=13, loc='lower right')

for spine in ax2.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

out_path2 = os.path.join(out_dir, 'h2_acc_frametype_pointplot.png')
fig2.savefig(out_path2, dpi=300, bbox_inches='tight')
print(f"Saved Hypothesis 2 Point Plot (95% CI) to {out_path2}")
plt.close(fig2)

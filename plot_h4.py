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
        conf_col = 'recogloop.conf_radio.response' if 'recogloop.conf_radio.response' in df.columns else 'conf_radio.response'
        
        if conf_col not in df.columns or 'target_img' not in df.columns:
            continue
            
        recog_trials = df.dropna(subset=[conf_col, 'target_img']).copy()
        if len(recog_trials) == 0:
            continue
            
        try:
             recog_trials[conf_col] = recog_trials[conf_col].astype(str).str.strip('[]').str.split(',').str[0]
             recog_trials[conf_col] = pd.to_numeric(recog_trials[conf_col], errors='coerce')
        except:
             pass

        valid_trials = recog_trials[recog_trials[conf_col].between(1, 5, inclusive='both')].copy()
        
        valid_trials['FrameType'] = valid_trials['target_img'].astype(str).apply(
            lambda x: 'Before Boundary (BB)' if 'BB' in x.upper() else ('Event Middle (EM)' if 'EM' in x.upper() else 'Unknown')
        )
        
        for frame_type in ['Before Boundary (BB)', 'Event Middle (EM)']:
            subset = valid_trials[valid_trials['FrameType'] == frame_type]
            if len(subset) > 0:
                conf = subset[conf_col].mean()
                results.append({
                    'Subject': sub_id,
                    'Condition': 'Natural Cut (NB)' if condition == 'NB' else 'Abrupt Cut (AB)',
                    'FrameType': frame_type,
                    'Confidence': conf
                })
                
    except Exception as e:
        print(f"Error processing {filename}: {e}")

df_res = pd.DataFrame(results)

print(f"Processed valid participant files for H4.")

print("Summary Statistics (Hypothesis 4):")

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

stats_df = df_res.groupby(['Condition', 'FrameType'])['Confidence'].apply(rich_stats).unstack()
print(stats_df)

out_dir = '/home/nikhil.repala/BRSM/Project/plots'
os.makedirs(out_dir, exist_ok=True)
stats_path = os.path.join(out_dir, 'h4_descriptive_stats.csv')
stats_df.to_csv(stats_path)
print(f"Saved descriptive statistics to {stats_path}")

palette = {'Natural Cut (NB)': '#4C72B0', 'Abrupt Cut (AB)': '#C44E52'}

plt.style.use('seaborn-v0_8-whitegrid')
fig1, ax1 = plt.subplots(figsize=(10, 7))
fig1.patch.set_facecolor('#ffffff')
ax1.set_facecolor('#f9f9f9')

sns.boxplot(data=df_res, x='FrameType', y='Confidence', hue='Condition', ax=ax1, 
            palette=palette, width=0.5, dodge=True, fliersize=0, linewidth=1.5, zorder=2)
sns.stripplot(data=df_res, x='FrameType', y='Confidence', hue='Condition', ax=ax1, 
              palette=palette, dodge=True, size=4, alpha=0.5, jitter=True, zorder=3)

handles, labels = ax1.get_legend_handles_labels()
ax1.legend(handles[:2], labels[:2], title='Video Condition', fontsize=12, title_fontsize=13, loc='lower right')

ax1.set_title('Confidence Distribution by Frame Type (Box + Points)', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('Participant Confidence Rating (1-5)', fontsize=14)
ax1.set_xlabel('Frame Type', fontsize=14)
ax1.set_ylim(1, 5.5)
ax1.tick_params(labelsize=12)

for spine in ax1.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

out_path1 = os.path.join(out_dir, 'h4_conf_frametype_boxstrip.png')
fig1.savefig(out_path1, dpi=300, bbox_inches='tight')
print(f"Saved Hypothesis 4 Box+Strip Plot to {out_path1}")
plt.close(fig1)

fig2, ax2 = plt.subplots(figsize=(8, 6))
fig2.patch.set_facecolor('#ffffff')
ax2.set_facecolor('#f9f9f9')

sns.pointplot(data=df_res, x='FrameType', y='Confidence', hue='Condition', ax=ax2, 
              palette=palette, dodge=True, markers=['o', 's'], capsize=.1, err_kws={'linewidth': 1.5})
            
ax2.set_title('Confidence Interaction: Frame Type x Condition (Point)', fontsize=16, fontweight='bold', pad=15)
ax2.set_ylabel('Mean Confidence Rating (1-5)', fontsize=14)
ax2.set_xlabel('Frame Type', fontsize=14)
ax2.set_ylim(3.8, 4.4) 
ax2.tick_params(labelsize=12)
ax2.legend(title='Video Condition', fontsize=12, title_fontsize=13, loc='lower right')

for spine in ax2.spines.values():
    spine.set_visible(True)
    spine.set_color('black')
    spine.set_linewidth(1.5)

out_path2 = os.path.join(out_dir, 'h4_conf_frametype_pointplot.png')
fig2.savefig(out_path2, dpi=300, bbox_inches='tight')
print(f"Saved Hypothesis 4 Point Plot to {out_path2}")
plt.close(fig2)

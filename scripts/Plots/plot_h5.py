import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import glob
import re

data_dir = '/home/nikhil.repala/BRSM/Project/BRSM data csv/BRSM data csv'
all_files = glob.glob(os.path.join(data_dir, '*.csv'))
demo_path = '/home/nikhil.repala/BRSM/Project/BRSM data csv/Demographic data.xlsx'

exclude_list = ['sub42_NB', 'sub151_NB', 'sub36_AB', 'sub161_NB', 'sub32_AB']

acc_results = []
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
        recog_trials = df.dropna(subset=[corr_col]).copy()
        if len(recog_trials) == 0:
            continue
        recog_trials[corr_col] = recog_trials[corr_col].astype(str).str.strip('[]').str.split(',').str[0]
        recog_trials[corr_col] = pd.to_numeric(recog_trials[corr_col], errors='coerce')
        acc = recog_trials[corr_col].mean()
        acc_results.append({'SubNum': sub_num, 'Condition': condition, 'Accuracy': acc})
    except Exception as e:
        print(f"Error: {filename}: {e}")

acc_df = pd.DataFrame(acc_results)

demo_df = pd.read_excel(demo_path)
demo_df.columns = demo_df.columns.astype(str).str.strip()

def extract_num(x):
    m = re.search(r'sub(\d+)_', str(x))
    return int(m.group(1)) if m else None

demo_df['SubNum'] = demo_df['Sub ID'].apply(extract_num)
demo_df = demo_df.dropna(subset=['SubNum'])
demo_df['SubNum'] = demo_df['SubNum'].astype(int)
demo_df = demo_df[demo_df['SubNum'] > 13]

exclude_nums = [42, 151, 36, 161, 32]
demo_df = demo_df[~demo_df['SubNum'].isin(exclude_nums)]

merged = acc_df.merge(demo_df, on='SubNum', how='inner')
merged['Gender'] = merged['Gender'].astype(str).str.strip().str.title()
merged['Handedness'] = merged['Handedness'].astype(str).str.strip().str.title()
merged['Vision'] = merged['Vision'].astype(str).str.strip().str.title()
merged['Age'] = pd.to_numeric(merged['Age'], errors='coerce')

print(f"Merged records: {len(merged)}")

out_dir = '/home/nikhil.repala/BRSM/Project/plots'
os.makedirs(out_dir, exist_ok=True)

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

stats = {
    'Gender': merged.groupby('Gender')['Accuracy'].apply(rich_stats).unstack(),
    'Handedness': merged.groupby('Handedness')['Accuracy'].apply(rich_stats).unstack(),
    'Vision': merged.groupby('Vision')['Accuracy'].apply(rich_stats).unstack(),
}

all_stats = pd.concat(stats, names=['Variable', 'Category'])
all_stats.to_csv(os.path.join(out_dir, 'h5_descriptive_stats.csv'))
print("Saved H5 descriptive stats.")
print(all_stats)

merged['AgeBin'] = pd.cut(merged['Age'], bins=[18, 21, 24, 27, 30], labels=['19-21', '22-24', '25-27', '28-30'])
age_stats = merged.groupby('AgeBin', observed=True)['Accuracy'].apply(rich_stats).unstack()
print("\nAge Group Stats:")
print(age_stats)
age_stats.to_csv(os.path.join(out_dir, 'h5_age_descriptive_stats.csv'))

age_clean = merged.dropna(subset=['Age'])
corr_val = age_clean['Age'].corr(age_clean['Accuracy'])
print(f"\nAge-Accuracy Pearson Correlation: {corr_val:.4f}")
blue = '#4C72B0'
red = '#C44E52'

fig1, ax1 = plt.subplots(figsize=(8, 6))
fig1.patch.set_facecolor('#ffffff')
ax1.set_facecolor('#f9f9f9')
plt.style.use('seaborn-v0_8-whitegrid')

gender_data = merged[merged['Gender'].isin(['Male', 'Female'])]
palette_g = {'Male': blue, 'Female': red}
sns.boxplot(data=gender_data, x='Gender', y='Accuracy', ax=ax1, palette=palette_g, width=0.45, fliersize=0, linewidth=1.5, zorder=2)
sns.stripplot(data=gender_data, x='Gender', y='Accuracy', ax=ax1, palette=palette_g, size=4, alpha=0.5, jitter=True, dodge=False, zorder=3)

ax1.set_title('Accuracy by Gender (H5)', fontsize=16, fontweight='bold', pad=15)
ax1.set_ylabel('Participant Accuracy (Proportion Correct)', fontsize=13)
ax1.set_xlabel('Gender', fontsize=13)
ax1.set_ylim(0.5, 1.05)
ax1.tick_params(labelsize=12)
for spine in ax1.spines.values():
    spine.set_visible(True); spine.set_color('black'); spine.set_linewidth(1.5)

fig1.savefig(os.path.join(out_dir, 'h5_gender_accuracy.png'), dpi=300, bbox_inches='tight')
print("Saved H5 Gender plot.")
plt.close(fig1)

fig2, ax2 = plt.subplots(figsize=(8, 6))
fig2.patch.set_facecolor('#ffffff')
ax2.set_facecolor('#f9f9f9')

age_clean = merged.dropna(subset=['Age'])
sns.regplot(data=age_clean, x='Age', y='Accuracy', ax=ax2, color=blue, scatter_kws={'alpha': 0.5, 's': 40}, line_kws={'linewidth': 2})

ax2.set_title('Accuracy by Age (H5)', fontsize=16, fontweight='bold', pad=15)
ax2.set_ylabel('Participant Accuracy (Proportion Correct)', fontsize=13)
ax2.set_xlabel('Age (years)', fontsize=13)
ax2.set_ylim(0.5, 1.05)
ax2.tick_params(labelsize=12)
for spine in ax2.spines.values():
    spine.set_visible(True); spine.set_color('black'); spine.set_linewidth(1.5)

fig2.savefig(os.path.join(out_dir, 'h5_age_accuracy.png'), dpi=300, bbox_inches='tight')
print("Saved H5 Age plot.")
plt.close(fig2)

fig3, ax3 = plt.subplots(figsize=(8, 6))
fig3.patch.set_facecolor('#ffffff')
ax3.set_facecolor('#f9f9f9')

hand_cats = [c for c in merged['Handedness'].unique() if c not in ['Nan', 'None']]
hand_palette = {cat: col for cat, col in zip(sorted(hand_cats), [blue, red, '#55A868'])}
hand_data = merged[merged['Handedness'].isin(hand_cats)]

sns.boxplot(data=hand_data, x='Handedness', y='Accuracy', ax=ax3, palette=hand_palette, width=0.45, fliersize=0, linewidth=1.5, zorder=2, order=sorted(hand_cats))
sns.stripplot(data=hand_data, x='Handedness', y='Accuracy', ax=ax3, palette=hand_palette, size=4, alpha=0.5, jitter=True, dodge=False, zorder=3, order=sorted(hand_cats))

ax3.set_title('Accuracy by Handedness (H5)', fontsize=16, fontweight='bold', pad=15)
ax3.set_ylabel('Participant Accuracy (Proportion Correct)', fontsize=13)
ax3.set_xlabel('Handedness', fontsize=13)
ax3.set_ylim(0.5, 1.05)
ax3.tick_params(labelsize=12)
for spine in ax3.spines.values():
    spine.set_visible(True); spine.set_color('black'); spine.set_linewidth(1.5)

fig3.savefig(os.path.join(out_dir, 'h5_handedness_accuracy.png'), dpi=300, bbox_inches='tight')
print("Saved H5 Handedness plot.")
plt.close(fig3)

fig4, ax4 = plt.subplots(figsize=(10, 6))
fig4.patch.set_facecolor('#ffffff')
ax4.set_facecolor('#f9f9f9')

vis_cats = [c for c in merged['Vision'].unique() if c not in ['Nan', 'None']]
vis_palette = {cat: col for cat, col in zip(sorted(vis_cats), [blue, red, '#55A868', '#8172B3'])}
vis_data = merged[merged['Vision'].isin(vis_cats)]

sns.boxplot(data=vis_data, x='Vision', y='Accuracy', ax=ax4, palette=vis_palette, width=0.45, fliersize=0, linewidth=1.5, zorder=2, order=sorted(vis_cats))
sns.stripplot(data=vis_data, x='Vision', y='Accuracy', ax=ax4, palette=vis_palette, size=4, alpha=0.5, jitter=True, dodge=False, zorder=3, order=sorted(vis_cats))

ax4.set_title('Accuracy by Vision Status (H5)', fontsize=16, fontweight='bold', pad=15)
ax4.set_ylabel('Participant Accuracy (Proportion Correct)', fontsize=13)
ax4.set_xlabel('Vision Status', fontsize=13)
ax4.set_ylim(0.5, 1.05)
ax4.tick_params(labelsize=12)
labels = [label.get_text() for label in ax4.get_xticklabels()]
ax4.set_xticklabels([l.replace('Corrected To Normal', 'Corrected\nTo Normal').replace('Uncorrected Vision Difficulty', 'Uncorrected\nDifficulty') for l in labels], fontsize=11)
for spine in ax4.spines.values():
    spine.set_visible(True); spine.set_color('black'); spine.set_linewidth(1.5)

fig4.savefig(os.path.join(out_dir, 'h5_vision_accuracy.png'), dpi=300, bbox_inches='tight')
print("Saved H5 Vision plot.")
plt.close(fig4)

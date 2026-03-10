import pandas as pd
import matplotlib.pyplot as plt
import os
import re

df = pd.read_excel('/home/nikhil.repala/BRSM/Project/BRSM data csv/Demographic data.xlsx')
df.columns = df.columns.astype(str).str.strip()

exclude = ['sub42_NB', 'sub151_NB', 'sub36_AB', 'sub161_NB', 'sub32_AB']
df = df[~df['Sub ID'].astype(str).str.strip().isin(exclude)]

def extract_num(x):
    match = re.search(r'sub(\d+)_', str(x))
    return int(match.group(1)) if match else 999

df['sub_num'] = df['Sub ID'].apply(extract_num)
df = df[df['sub_num'] > 13]

plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.patch.set_facecolor('#ffffff')
for i, ax in enumerate(axes.flatten()):
    ax.set_facecolor('#f9f9f9')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(2.0)
    
    ax.margins(0.15)

age_col = pd.to_numeric(df['Age'], errors='coerce').dropna()
axes[0, 0].hist(age_col, bins=10, color='#4C72B0', edgecolor='black', linewidth=1.2)
axes[0, 0].set_title('Participant Age Distribution', fontsize=16, fontweight='bold', pad=15)
axes[0, 0].set_xlabel('Age', fontsize=14)
axes[0, 0].set_ylabel('Count', fontsize=14)
axes[0, 0].tick_params(labelsize=12)

gender_counts = df['Gender'].str.strip().str.title().value_counts()
axes[0, 1].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', 
        colors=['#4C72B0', '#DD8452'], startangle=90, textprops={'fontsize': 14},
        wedgeprops={'edgecolor': 'black', 'linewidth': 1})
axes[0, 1].set_title('Participant Gender Distribution', fontsize=16, fontweight='bold', pad=15)
axes[0, 1].set_xticks([])
axes[0, 1].set_yticks([])

handedness_counts = df['Handedness'].str.strip().str.title().value_counts()
axes[1, 0].pie(handedness_counts, labels=handedness_counts.index, autopct='%1.1f%%', 
        colors=['#55A868', '#C44E52'], startangle=90, textprops={'fontsize': 14},
        wedgeprops={'edgecolor': 'black', 'linewidth': 1})
axes[1, 0].set_title('Participant Handedness', fontsize=16, fontweight='bold', pad=15)
axes[1, 0].set_xticks([])
axes[1, 0].set_yticks([])

vision_counts = df['Vision'].str.strip().str.title().value_counts()
labels = vision_counts.index.tolist()
labels = [l.replace('Uncorrected Vision Difficulty', 'Uncorrected\nDifficulty') for l in labels]
axes[1, 1].pie(vision_counts, labels=labels, autopct='%1.1f%%', 
        colors=['#55A868', '#C44E52', '#8172B3'], startangle=140, textprops={'fontsize': 14},
        wedgeprops={'edgecolor': 'black', 'linewidth': 1})
axes[1, 1].set_title('Participant Vision Status', fontsize=16, fontweight='bold', pad=15)
axes[1, 1].set_xticks([])
axes[1, 1].set_yticks([])

plt.tight_layout(pad=4.0, w_pad=4.0, h_pad=4.0)

out_dir = '/home/nikhil.repala/BRSM/Project/plots'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'demographics_summary.png')
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Saved cleanly bordered plots to {out_path}")

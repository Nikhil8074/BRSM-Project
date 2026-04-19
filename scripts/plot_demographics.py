import pandas as pd
import matplotlib.pyplot as plt
import os

# 1. Load the imputed demographic data
data_path = './BRSM data csv/Imputed Demographics.csv'
df = pd.read_csv(data_path)

# 2. Setup Plotting Style
plt.style.use('seaborn-v0_8-whitegrid')
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.patch.set_facecolor('#ffffff')

# Colors - Professional Palette
COLORS = ['#4C72B0', '#DD8452', '#55A868', '#C44E52', '#8172B3']

# Helper to format axes
for ax in axes.flatten():
    ax.set_facecolor('#f9f9f9')
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1.5)

# A. Age Distribution
axes[0, 0].hist(df['Age'], bins=10, color=COLORS[0], edgecolor='black', linewidth=1.2)
axes[0, 0].set_title('Participant Age Distribution', fontsize=16, fontweight='bold', pad=15)
axes[0, 0].set_xlabel('Age', fontsize=14)
axes[0, 0].set_ylabel('Count', fontsize=14)

# B. Gender Distribution
gender_counts = df['Gender'].value_counts()
axes[0, 1].pie(gender_counts, labels=gender_counts.index, autopct='%1.1f%%', 
              colors=[COLORS[0], COLORS[1]], startangle=90, 
              textprops={'fontsize': 14}, wedgeprops={'edgecolor': 'black', 'linewidth': 1})
axes[0, 1].set_title('Participant Gender Distribution', fontsize=16, fontweight='bold', pad=15)

# C. Handedness Distribution
hand_counts = df['Handedness'].value_counts()
axes[1, 0].pie(hand_counts, labels=hand_counts.index, autopct='%1.1f%%', 
              colors=[COLORS[2], COLORS[3]], startangle=90, 
              textprops={'fontsize': 14}, wedgeprops={'edgecolor': 'black', 'linewidth': 1})
axes[1, 0].set_title('Participant Handedness', fontsize=16, fontweight='bold', pad=15)

# D. Vision Status
vision_counts = df['Vision'].value_counts()
labels = [l.replace('Uncorrected vision difficulty', 'Uncorrected\nDifficulty') for l in vision_counts.index]
axes[1, 1].pie(vision_counts, labels=labels, autopct='%1.1f%%', 
              colors=[COLORS[2], COLORS[3], COLORS[4]], startangle=140, 
              textprops={'fontsize': 14}, wedgeprops={'edgecolor': 'black', 'linewidth': 1})
axes[1, 1].set_title('Participant Vision Status', fontsize=16, fontweight='bold', pad=15)

# 3. Final Layout and Save
plt.tight_layout(pad=4.0)
out_path = 'demographics_summary.png'  # Save to root for report reference
plt.savefig(out_path, dpi=300, bbox_inches='tight')
print(f"Successfully saved imputed demographic plot to: {out_path}")

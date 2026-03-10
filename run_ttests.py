import pandas as pd
import numpy as np
from scipy import stats
import os
import glob
import re


data_dir = '/home/nikhil.repala/BRSM/Project/BRSM data csv/BRSM data csv'
demo_path = '/home/nikhil.repala/BRSM/Project/BRSM data csv/Demographic data.xlsx'
all_files = glob.glob(os.path.join(data_dir, '*.csv'))
exclude_list = ['sub42_NB', 'sub151_NB', 'sub36_AB', 'sub161_NB', 'sub32_AB']
out_dir = '/home/nikhil.repala/BRSM/Project/plots'
os.makedirs(out_dir, exist_ok=True)

def run_ttest(group1, group2, label, tail='two-sided'):
    """Run an independent samples t-test and print the result."""
    g1 = group1.dropna()
    g2 = group2.dropna()
    t_stat, p_two = stats.ttest_ind(g1, g2, equal_var=False)
    if tail == 'greater':
        p = p_two / 2 if t_stat > 0 else 1 - p_two / 2
        tail_label = 'one-tailed (greater)'
    elif tail == 'less':
        p = p_two / 2 if t_stat < 0 else 1 - p_two / 2
        tail_label = 'one-tailed (less)'
    else:
        p = p_two
        tail_label = 'two-tailed'
    sig = '***' if p < 0.001 else ('**' if p < 0.01 else ('*' if p < 0.05 else 'ns'))
    print(f"  {label}")
    print(f"    n1={len(g1)}, n2={len(g2)}, M1={g1.mean():.4f}, M2={g2.mean():.4f}")
    print(f"    t = {t_stat:.4f},  p ({tail_label}) = {p:.4f}  {sig}")
    return {'label': label, 'n1': len(g1), 'n2': len(g2),
            'M1': g1.mean(), 'SD1': g1.std(), 'M2': g2.mean(), 'SD2': g2.std(),
            't': t_stat, 'p': p, 'tail': tail_label, 'sig': sig}

records = []
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
        corr_col  = 'recogloop.resp.corr'   if 'recogloop.resp.corr'   in df.columns else 'resp.corr'
        rt_col    = 'recogloop.resp.rt'      if 'recogloop.resp.rt'     in df.columns else 'resp.rt'
        conf_col  = 'recogloop.conf_radio.response' if 'recogloop.conf_radio.response' in df.columns else 'conf_radio.response'

        trials = df.dropna(subset=[corr_col]).copy()
        trials[corr_col] = pd.to_numeric(trials[corr_col].astype(str).str.strip('[]').str.split(',').str[0], errors='coerce')
        trials[rt_col]   = pd.to_numeric(trials[rt_col].astype(str).str.strip('[]').str.split(',').str[0], errors='coerce')
        if conf_col in trials.columns:
            trials[conf_col] = pd.to_numeric(trials[conf_col].astype(str).str.strip('[]').str.split(',').str[0], errors='coerce')

        if 'target_img' in df.columns:
            trials['FrameType'] = trials['target_img'].astype(str).apply(
                lambda x: 'BB' if 'BB' in x.upper() else ('EM' if 'EM' in x.upper() else 'Unknown'))

        records.append({'sub_id': sub_id, 'sub_num': sub_num, 'condition': condition, 'trials': trials})
    except Exception as e:
        print(f"  Error: {filename}: {e}")

print(f"Loaded {len(records)} participant files.\n")
all_results = {}

print("=" * 60)
print("HYPOTHESIS 1: Overall Accuracy & Response Time")
print("=" * 60)
h1_rows = []
for r in records:
    t = r['trials']
    acc = t[t.columns[t.columns.str.contains('resp.corr')][0]].mean()
    rt_col_name = [c for c in t.columns if 'resp.rt' in c and 'recogloop' in c]
    rt = t[rt_col_name[0]].dropna().mean() if rt_col_name else np.nan
    h1_rows.append({'condition': r['condition'], 'Accuracy': acc, 'RT': rt})

h1 = pd.DataFrame(h1_rows)
nb_acc = h1[h1.condition=='NB']['Accuracy']
ab_acc = h1[h1.condition=='AB']['Accuracy']
nb_rt  = h1[h1.condition=='NB']['RT']
ab_rt  = h1[h1.condition=='AB']['RT']

res1 = []
res1.append(run_ttest(nb_acc, ab_acc, "Accuracy: NB > AB (H0: no diff)", tail='greater'))
res1.append(run_ttest(nb_rt, ab_rt,   "Response Time: NB < AB (H0: no diff)", tail='less'))
pd.DataFrame(res1).to_csv(os.path.join(out_dir, 'h1_ttest_results.csv'), index=False)
print("  -> Saved: h1_ttest_results.csv\n")

print("=" * 60)
print("HYPOTHESIS 2: Accuracy Across Frame Types")
print("=" * 60)
h2_rows = []
for r in records:
    t = r['trials']
    if 'FrameType' not in t.columns:
        continue
    corr_col = [c for c in t.columns if 'resp.corr' in c][0]
    for ft in ['BB', 'EM']:
        sub = t[t['FrameType'] == ft]
        acc = sub[corr_col].mean()
        h2_rows.append({'condition': r['condition'], 'FrameType': ft, 'Accuracy': acc})

h2 = pd.DataFrame(h2_rows)
res2 = []
for ft, label in [('BB', 'Before Boundary'), ('EM', 'Event Middle')]:
    nb = h2[(h2.condition=='NB') & (h2.FrameType==ft)]['Accuracy']
    ab = h2[(h2.condition=='AB') & (h2.FrameType==ft)]['Accuracy']
    tail = 'greater' if ft == 'BB' else 'two-sided'
    res2.append(run_ttest(nb, ab, f"Accuracy ({label}): NB vs AB", tail=tail))

pd.DataFrame(res2).to_csv(os.path.join(out_dir, 'h2_ttest_results.csv'), index=False)
print("  -> Saved: h2_ttest_results.csv\n")

print("=" * 60)
print("HYPOTHESIS 3: Confidence and Correctness")
print("=" * 60)
h3_rows = []
for r in records:
    t = r['trials']
    conf_cols = [c for c in t.columns if 'conf_radio.response' in c]
    corr_cols = [c for c in t.columns if 'resp.corr' in c]
    if not conf_cols or not corr_cols:
        continue
    cf, cr = conf_cols[0], corr_cols[0]
    valid = t[t[cf].between(1, 5, inclusive='both')].copy()
    valid['Correct'] = pd.to_numeric(valid[cr], errors='coerce')
    for correctness in [1, 0]:
        sub = valid[valid['Correct'] == correctness]
        conf_mean = sub[cf].mean()
        label = 'Correct' if correctness == 1 else 'Incorrect'
        h3_rows.append({'condition': r['condition'], 'Correctness': label, 'Confidence': conf_mean})

h3 = pd.DataFrame(h3_rows)
res3 = []
for corr_label, tail in [('Correct', 'greater'), ('Incorrect', 'two-sided')]:
    nb = h3[(h3.condition=='NB') & (h3.Correctness==corr_label)]['Confidence']
    ab = h3[(h3.condition=='AB') & (h3.Correctness==corr_label)]['Confidence']
    res3.append(run_ttest(nb, ab, f"Confidence ({corr_label} Responses): NB vs AB", tail=tail))

pd.DataFrame(res3).to_csv(os.path.join(out_dir, 'h3_ttest_results.csv'), index=False)
print("  -> Saved: h3_ttest_results.csv\n")

print("=" * 60)
print("HYPOTHESIS 4: Confidence Calibration Across Frame Types")
print("=" * 60)
h4_rows = []
for r in records:
    t = r['trials']
    conf_cols = [c for c in t.columns if 'conf_radio.response' in c]
    if not conf_cols or 'FrameType' not in t.columns:
        continue
    cf = conf_cols[0]
    valid = t[t[cf].between(1, 5, inclusive='both')].copy()
    for ft in ['BB', 'EM']:
        sub = valid[valid['FrameType'] == ft]
        conf_mean = sub[cf].mean()
        h4_rows.append({'condition': r['condition'], 'FrameType': ft, 'Confidence': conf_mean})

h4 = pd.DataFrame(h4_rows)
res4 = []
for ft, label in [('BB', 'Before Boundary'), ('EM', 'Event Middle')]:
    nb = h4[(h4.condition=='NB') & (h4.FrameType==ft)]['Confidence']
    ab = h4[(h4.condition=='AB') & (h4.FrameType==ft)]['Confidence']
    tail = 'greater' if ft == 'BB' else 'two-sided'
    res4.append(run_ttest(nb, ab, f"Confidence ({label}): NB vs AB", tail=tail))

pd.DataFrame(res4).to_csv(os.path.join(out_dir, 'h4_ttest_results.csv'), index=False)
print("  -> Saved: h4_ttest_results.csv\n")

print("=" * 60)
print("HYPOTHESIS 5: Demographic Factors (Gender)")
print("=" * 60)

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

h5_acc = []
for r in records:
    t = r['trials']
    corr_col = [c for c in t.columns if 'resp.corr' in c][0]
    acc = t[corr_col].mean()
    h5_acc.append({'SubNum': r['sub_num'], 'Accuracy': acc})

h5_acc_df = pd.DataFrame(h5_acc)
merged = h5_acc_df.merge(demo_df, on='SubNum', how='inner')
merged['Gender'] = merged['Gender'].astype(str).str.strip().str.title()
merged['Handedness'] = merged['Handedness'].astype(str).str.strip().str.title()

res5 = []
male_acc   = merged[merged['Gender']=='Male']['Accuracy']
female_acc = merged[merged['Gender']=='Female']['Accuracy']
res5.append(run_ttest(male_acc, female_acc, "Accuracy: Male vs Female", tail='two-sided'))
right_acc = merged[merged['Handedness']=='Right Handed']['Accuracy']
left_acc  = merged[merged['Handedness']=='Left Handed']['Accuracy']
res5.append(run_ttest(right_acc, left_acc, "Accuracy: Right-Handed vs Left-Handed", tail='two-sided'))

pd.DataFrame(res5).to_csv(os.path.join(out_dir, 'h5_ttest_results.csv'), index=False)
print("  -> Saved: h5_ttest_results.csv\n")

print("=" * 60)
print("All t-test results have been saved to the plots/ directory.")
print("=" * 60)

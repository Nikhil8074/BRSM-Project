import pandas as pd
import numpy as np

exclude = ['sub42_NB', 'sub151_NB', 'sub36_AB', 'sub161_NB', 'sub32_AB']

df = pd.read_excel('/home/nikhil.repala/BRSM/Project/BRSM data csv/Demographic data.xlsx')

df.columns = df.columns.astype(str).str.strip()

df = df[~df['Sub ID'].astype(str).str.strip().isin(exclude)]

import re
def extract_num(x):
    match = re.search(r'sub(\d+)_', str(x))
    return int(match.group(1)) if match else 999

df['sub_num'] = df['Sub ID'].apply(extract_num)
df = df[df['sub_num'] > 13]

print(f"Total Participants Retained: {len(df)}")

if 'Age' in df.columns:
    age_col = pd.to_numeric(df['Age'], errors='coerce')
    print(f"Age: Mean={age_col.mean():.2f}, SD={age_col.std():.2f}, Range={age_col.min()}-{age_col.max()}")
    
if 'Gender' in df.columns:
    print("\nGender:")
    print(df['Gender'].str.strip().str.title().value_counts())
    
if 'Handedness' in df.columns:
    print("\nHandedness:")
    print(df['Handedness'].str.strip().str.title().value_counts())

if 'Vision' in df.columns:
    print("\nVision:")
    print(df['Vision'].str.strip().str.title().value_counts())

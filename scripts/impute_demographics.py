import pandas as pd
import numpy as np
from analytical_utils import load_participant_data

def impute_demographics():
    print("--- Demographic Imputation & Summary ---")
    
    # 1. Get the list of 166 SubIDs in our analysis
    records = load_participant_data()
    valid_ids = [r['sub_id'] for r in records]
    
    # 2. Load Demographic Data
    df = pd.read_excel('./BRSM data csv/Demographic data.xlsx')
    df.columns = [c.strip() for c in df.columns]
    df['Sub ID'] = df['Sub ID'].str.strip()
    
    # 3. Filter to the 166 analyzed participants
    df_filtered = df[df['Sub ID'].isin(valid_ids)].copy()
    print(f"Filtering to analyzed sample: {len(df_filtered)} participants.")
    
    # 4. Impute Missing Values
    # Age: Mean
    avg_age = df_filtered['Age'].mean()
    df_filtered['Age'] = df_filtered['Age'].fillna(avg_age)
    
    # Gender: Mode
    gender_mode = df_filtered['Gender'].mode()[0]
    df_filtered['Gender'] = df_filtered['Gender'].fillna(gender_mode)
    
    # Handedness: Mode
    hand_mode = df_filtered['Handedness'].mode()[0]
    df_filtered['Handedness'] = df_filtered['Handedness'].fillna(hand_mode)
    
    # Vision: Mode
    vision_mode = df_filtered['Vision'].mode()[0]
    df_filtered['Vision'] = df_filtered['Vision'].fillna(vision_mode)
    
    print("\n[Imputation Results]")
    print(f"  Age imputed with mean: {avg_age:.2f}")
    print(f"  Gender imputed with mode: {gender_mode}")
    print(f"  Handedness imputed with mode: {hand_mode}")
    print(f"  Vision imputed with mode: {vision_mode}")
    
    # 5. Generate Stats for Report
    print("\n[Updated Demographic Summary]")
    print(f"Age: Mean={df_filtered['Age'].mean():.2f}, SD={df_filtered['Age'].std():.2f}")
    print(f"Age Range: {df_filtered['Age'].min():.2f} - {df_filtered['Age'].max():.2f}")
    
    print("\nGender Counts:")
    print(df_filtered['Gender'].value_counts())
    
    print("\nHandedness Counts:")
    print(df_filtered['Handedness'].value_counts())
    
    print("\nVision Status Counts:")
    print(df_filtered['Vision'].value_counts())
    
    # Save the imputed data for the subsequent H5 analysis
    df_imputed = df_filtered.copy()

    # 6. Add the 4 participants entirely missing from the demographic file
    missing_ids = [i for i in valid_ids if i not in df_filtered['Sub ID'].tolist()]
    print(f"\nAdding {len(missing_ids)} missing participants with imputed values: {missing_ids}")
    
    missing_rows = []
    for mid in missing_ids:
        missing_rows.append({
            'Sub ID': mid,
            'Age': df_filtered['Age'].mean(),
            'Gender': df_filtered['Gender'].mode()[0],
            'Handedness': df_filtered['Handedness'].mode()[0],
            'Vision': df_filtered['Vision'].mode()[0]
        })
    
    df_final = pd.concat([df_imputed, pd.DataFrame(missing_rows)], ignore_index=True)
    print(f"Final imputed sample size: {len(df_final)}")

    # 7. Generate Final Stats for Report
    print("\n[Final Demographic Summary (N=166)]")
    print(f"Age: Mean={df_final['Age'].mean():.2f}, SD={df_final['Age'].std():.2f}")
    print(f"Age Range: {df_final['Age'].min():.2f} - {df_final['Age'].max():.2f}")
    
    print("\nGender Counts:")
    print(df_final['Gender'].value_counts())
    
    print("\nHandedness Counts:")
    print(df_final['Handedness'].value_counts())
    
    print("\nVision Status Counts:")
    print(df_final['Vision'].value_counts())

    df_final.to_csv('./BRSM data csv/Imputed Demographics.csv', index=False)
    print("\nSaved final imputed data to: './BRSM data csv/Imputed Demographics.csv'")

if __name__ == "__main__":
    impute_demographics()

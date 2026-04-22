import pandas as pd
import statsmodels.formula.api as smf
from analytical_utils import load_participant_data

def run_analysis():
    print("\n--- [H5] Demographic Effects (Multiple Regression) ---")
    
    # 1. Load Behavioral Data
    records = load_participant_data()
    participant_summary = []
    
    for r in records:
        df = r['trials']
        participant_summary.append({
            'SubID': r['sub_id'],
            'Condition': r['condition'],
            'Accuracy': df[r['corr_col']].mean()
        })
        
    df_participants = pd.DataFrame(participant_summary)
    
    # 2. Load and Merge Demographics
    demo_df = pd.read_csv('./BRSM data csv/Imputed Demographics.csv')
    df_demo_merged = pd.merge(df_participants, demo_df, left_on='SubID', right_on='Sub ID', how='inner')
    
    # Standardize factors
    df_demo_merged['Vision_Simple'] = df_demo_merged['Vision'].astype(str).str.lower().str.contains('corrected').map({True: 'Corrected', False: 'Normal'})
    df_demo_merged['Hand_Simple'] = df_demo_merged['Handedness'].astype(str).str.lower().apply(lambda x: 'right' if 'right' in x else 'left')
    df_demo_merged['Gender_Simple'] = df_demo_merged['Gender'].astype(str).str.lower()
    
    # 3. Regression Analysis
    model = smf.ols('Accuracy ~ C(Condition, Treatment("NB")) + Age + C(Gender_Simple) + C(Hand_Simple) + C(Vision_Simple)', data=df_demo_merged).fit()
    print(model.summary().tables[1])

if __name__ == "__main__":
    run_analysis()

import pandas as pd

def check_required_columns(output_file="data/training_results.csv"):
    df = pd.read_csv(output_file)
    required_columns = ["id", "eom", "w"]
    if not all(col in df.columns for col in required_columns):
        return False, "Output does not contain required columns (id, eom, w)"
    else:
        return True, "Required Columns Check Passed!"

def compare_columns(output_file="data/training_results.csv", chars_file="data/ctff_chars.parquet"):
    
    chars = pd.read_parquet(chars_file)
    output = pd.read_csv(output_file)
        
    # Filter DataFrames and select relevant columns
    chars_filtered = chars.loc[chars['ctff_test'] == True, ['id', 'eom']]
    output_filtered = output[['id', 'eom']]

    # Convert 'output' columns to match 'chars' data types
    chars_id_dtype = chars_filtered['id'].dtype
    output_filtered.loc[:, 'id'] = output_filtered['id'].astype(chars_id_dtype)

    # Normalize 'eom' column by converting both to datetime without time components
    output_filtered.loc[:, 'eom'] = pd.to_datetime(output_filtered['eom']).dt.date
    chars_filtered.loc[:, 'eom'] = pd.to_datetime(chars_filtered['eom']).dt.date

    # Sort both DataFrames by 'id' and 'eom'
    output_cols_sorted = output_filtered.sort_values(by=['id', 'eom']).reset_index(drop=True)
    chars_cols_sorted = chars_filtered.sort_values(by=['id', 'eom']).reset_index(drop=True)

    # Compare the 'id' and 'eom' columns
    if chars_cols_sorted.equals(output_cols_sorted):
        return True, "Columns match the required format."
    else:
        return False, "Columns do not match the required format."
    
def calculate_sharpe_ratio():
    try:
        #calculating sharpe:
        chars = pd.read_parquet("data/ctff_chars.parquet")
        pf= pd.read_csv("data/training_results.csv")
        
        #getting rets attached to weights
        sharpe_df = pd.merge(
            pf.assign(
                id=pf['id'].astype('int64'),
                eom=pd.to_datetime(pf['eom']),
                w=pf['w'].astype('float64')
            )[['id', 'eom', 'w']],
            chars.assign(
                id=chars['id'].astype('int64'),
                eom=pd.to_datetime(chars['eom']),
                ret_exc_lead1m=chars['ret_exc_lead1m'].astype('float64')
            )[['id', 'eom', 'ret_exc_lead1m']],
            on=['id', 'eom'],
            how='left'
        )

        # Calculate weighted returns
        sharpe_df['w_ret'] = sharpe_df['w'] * sharpe_df['ret_exc_lead1m']

        # Group by eom and calculate the sum of products
        rets = sharpe_df.groupby('eom')['w_ret'].sum()

        # Calculate average and volatility
        average_ret = rets.mean()
        volatility = rets.std()

        # calculate sharpe
        sharpe = average_ret/volatility

        return True, str(sharpe)

    except Exception as e:
        return False, str(e)
    

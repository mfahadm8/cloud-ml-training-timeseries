import pandas as pd

def check_required_columns(output_file="data/training_results.csv"):
    df = pd.read_csv(output_file)
    required_columns = ["id", "eom", "w"]
    if not all(col in df.columns for col in required_columns):
        return False, "Output does not contain required columns (id, eom, w)"
    else:
        return True, "Required Columns Check Passed!"

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
    

import pandas as pd
import xgboost as xgb

# Define necessary functions
def ecdf(data):
    """ Compute the empirical cumulative distribution function for a pandas Series. """
    if data.empty:
        return data
    sorted_data = data.sort_values()
    ranks = sorted_data.rank(method='min', pct=True)
    cdf_values = ranks
    return pd.Series(cdf_values, index=data.index)

def prepare_data(chars, features, eom):
    """ Prepare the data by applying an ECDF transformation grouped by 'eom',
    while preserving zeros and imputing missing values with 0.5. """
    for feature in features:
        is_zero = chars[feature] == 0  # Preserve zeros
        chars[feature] = chars.groupby(eom)[feature].transform(lambda x: ecdf(x))
        chars.loc[is_zero, feature] = 0  # Restore zeros
        chars[feature].fillna(0.5, inplace=True)  # Impute missing values
    return chars

def fit_xgb(train, features):
    """ Train an XGBoost model on the training data. """
    dtrain = xgb.DMatrix(data=train[features], label=train['ret_exc_lead1m'])
    params = {
        'booster': 'gbtree',
        'eta': 0.1,
        'max_depth': 3,
        'subsample': 0.5,
        'colsample_bytree': 0.5,
        'objective': 'reg:squarederror',
        'verbosity': 0
    }
    model = xgb.train(params, dtrain, num_boost_round=100)
    return model

def load_data()->(str): 
    """ Placeholder function for data loading. """
    features = pd.read_parquet("data/ctff_features.parquet")['features']
    chars = pd.read_parquet("data/ctff_chars.parquet")
    return features, chars
    # raise NotImplementedError("This function should be replaced by the bash script.") # should return features, chars tuple, Also, Template should not allow nested funtions inside load_data()

def export_data(pf):
    """ Placeholder function for data exporting. """
    pf.to_parquet("data/portfolio.parquet")
    # raise NotImplementedError("This function should be replaced by the bash script.") # Template should not allow nested funtions inside export_data()

def main(chars, features, eom='eom'):
    """ Main function to orchestrate data preparation, model training, and calculating weights. """
    chars = prepare_data(chars, features, eom)
    
    train = chars[chars['ctff_test'] == False]
    test = chars[chars['ctff_test'] == True]
    
    model = fit_xgb(train, features)
    
    dtest = xgb.DMatrix(test[features])
    test['pred'] = model.predict(dtest)
    
    test['rank'] = test.groupby(eom)['pred'].rank(ascending=False, method='average')
    test['rank'] = test.groupby(eom)['rank'].transform(lambda x: x - x.mean())
    test['w'] = test.groupby(eom)['rank'].transform(lambda x: x / x.abs().sum() * 2)
    
    return test[['id', eom, 'w']]

# Logic to execute when script is directly run
if __name__ == "__main__":
    features, chars = load_data()
    pf = main(chars, features)
    export_data(pf)
    

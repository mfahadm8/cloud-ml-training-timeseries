def load_data()->(str): 
    """ Placeholder function for data loading. """
    features = pd.read_parquet("integrity-check/ctff_features_integrity.parquet")['features']
    chars = pd.read_parquet("integrity-check/ctff_chars_integrity.parquet")
    daily_ret = pd.read_parquet("integrity-check/ctff_daily_ret.parquet")
    return features, chars,daily_ret

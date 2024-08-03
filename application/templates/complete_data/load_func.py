def load_data()->(str): 
    """ Placeholder function for data loading. """
    features = pd.read_parquet("data/ctff_features.parquet")['features']
    chars = pd.read_parquet("data/ctff_chars.parquet")
    daily_ret = pd.read_parquet("data/ctff_daily_ret.parquet")
    return features, chars, daily_ret

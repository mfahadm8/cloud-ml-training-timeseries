def load_data()->(str): 
    """ Placeholder function for data loading. """
    features = pd.read_parquet("integrity-check/ctff_features.parquet")['features']
    chars = pd.read_parquet("integrity-check/ctff_chars.parquet")
    return features, chars

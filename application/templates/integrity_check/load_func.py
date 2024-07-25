def load_data()->(str): 
    """ Placeholder function for data loading. """
    features = pd.read_parquet("integrity-check/ctff_features_integrity.parquet")['features']
    chars = pd.read_parquet("integrity-check/ctff_chars_integrity.parquet")
    return features, chars

from feature_engineering.data_pipeline import *


"""Initialize the feature engineering class!"""
itu = FeatureEngineering()


"""
Call opendata classes of features listed in configs.FEATURES, join them to schools  
"""
itu.set_training_data()


"""
Saves the complete dataset!
"""
itu.save_training_set()


"""
Call opendata classes of features listed in configs.FEATURES and return raw data as dictionary with feature names as keys   
"""
opendata = itu.get_opendata()

"""load data_pipeline"""
from feature_engineering.data_pipeline import *


"""Initialize the feature engineering class; set the school data"""
itu = FeatureEngineering()


"""Shows the school dataset"""
# itu.school_data 


"""Calls OpenData classes of features listed in configs.FEATURES, joins them to school data"""
itu.set_training_data()


"""Saves the training set with features"""
itu.save_training_set()


"""Calls OpenData classes of features listed in configs.FEATURES and returns dictionary with feature names as keys and datasets as values"""
opendata = itu.get_opendata()
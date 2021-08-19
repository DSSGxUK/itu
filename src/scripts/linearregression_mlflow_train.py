# load libraries
import yaml
import mlflow
import pandas as pd
import numpy as np
import xgboost as xgb
import subprocess

from mlflow.sklearn import log_model
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV, GridSearchCV, cross_val_score
from sklearn.metrics import make_scorer, mean_absolute_error, mean_squared_error, r2_score
from datetime import datetime, date

# start time
begin_time = datetime.now()

# read in (yaml) configs
with open('../../conf/model_config.yaml', 'r') as conf:
    model_config = yaml.safe_load(conf)

print("#####################################################")
print("Model config file loaded")
print("#####################################################")

#### mlflow setup ####

# save runs
mlflow.set_tracking_uri("file:///files/mlruns")
mlflow.tracking.get_tracking_uri()

#Naming the set_experiment
dt = date.today().strftime('%d/%m/%Y')
experiment_name = dt + model_config['meta']['experiment_name']
mlflow.set_experiment(experiment_name)
mlflow_client = mlflow.tracking.MlflowClient()
experiment_id = mlflow_client.get_experiment_by_name(experiment_name).experiment_id

print("#####################################################")
print("Experiment_id:",experiment_id)
print("Experiment_name:", experiment_name)
print("#####################################################")

# import data
dataset = '../../' + model_config['model']['loc'] + model_config['model']['file']
dataset = pd.read_csv(dataset)

print("#####################################################")
print("training data loaded")
print("#####################################################")

# define predictors and target
pred   = model_config['meta']['predictors']
target = model_config['meta']['target']

# subset data
X = dataset[pred]
y = dataset[target]

#Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y,
test_size = model_config['parameter']['test_size'], random_state = 42)

print("#####################################################")
print("size of training dataset = ", len(X_train))
print("size of hold out dataset = ", len(X_test))
print("#####################################################")

#Defining the model
model = LinearRegression()

#Logging metrics with mlflow
with mlflow.start_run(run_name = model_config['meta']['run_name']) as run:

    #Fitting the Model
    model.fit(X_train, y_train)
    print('Fitting...')

    # Run the 3-fold cross validation
    scores = cross_val_score(
        model,
        X_train,
        y_train,
        cv=model_config['parameter']['inner_cv'],
    )

    # Report
    print('Cross validation scores on training:')
    print("R^2 scores = ", scores)
    print("Scores mean = ", scores.mean())
    print("Score std dev = ", scores.std())

    #Creating predictions
    y_pred = model.predict(X_test)

    #Test Scores
    print('Test Metrics:')
    print("MAE", mean_absolute_error(y_test, y_pred))
    print("R2", r2_score(y_test, y_pred))

    log_model(model, 'model')
    mlflow.log_metric("MAE", mean_absolute_error(y_test, y_pred))
    mlflow.log_metric("MSE", mean_squared_error(y_test, y_pred, squared=True))
    mlflow.log_metric("RMSE", mean_squared_error(y_test, y_pred, squared=False))
    mlflow.log_metric("R2", r2_score(y_test, y_pred))
    #mlflow.log_metric("MAPE", 100*np.mean(abs(y_pred - y_test)/ y_test))

mlflow.end_run()

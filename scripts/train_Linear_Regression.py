#Load Packages
from __future__ import print_function
#preprocessing
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
#model selection
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression

#model fit
from sklearn.model_selection import train_test_split
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import RandomizedSearchCV


#Metrics
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn import datasets, linear_model
#mlflow
import mlflow
from mlflow.sklearn import log_model
#other packages
import numpy as np
import pandas as pd
import geopandas as gpd
import yaml
from pprint import pprint
from datetime import date, datetime, time, tzinfo, timedelta

# save runs
mlflow.set_tracking_uri("file:///files/mlruns")
mlflow.tracking.get_tracking_uri()

#Implementing start time
begin_time = datetime.now()
print("Run Start:",begin_time)

#Alternative which is using model_conf file with FE.py script
#read in (yaml) configs
with open('../../conf/model_config.yaml', 'r') as conf:
    model_config = yaml.safe_load(conf)
print("Model config file opened")

#Mlflow VERSION
print("MLflow Version:",mlflow.version.VERSION)
print("MLflow Tracking URI:", mlflow.get_tracking_uri())

#Naming the set_experiment
dt = date.today().strftime('%d/%m/%Y')
experiment_name= dt + model_config['meta']['experiment_name']

mlflow.set_experiment(experiment_name)
mlflow_client = mlflow.tracking.MlflowClient()
experiment_id = mlflow_client.get_experiment_by_name(experiment_name).experiment_id
print("Experiment_id:",experiment_id)
print("Experiment_name:", experiment_name)

# Get Experiment Details
experiment = mlflow.get_experiment_by_name(experiment_name)
print("Experiment_id: {}".format(experiment.experiment_id))
print("Artifact Location: {}".format(experiment.artifact_location))
print("Tags: {}".format(experiment.tags))
print("Lifecycle_stage: {}".format(experiment.lifecycle_stage))

# fit model
# Import Data Table
#dataset = model_config['meta'][2]['loc_file'] + model_config['meta']['file_name']
dataset = model_config['model']['loc'] + model_config['model']['file']
dataset= pd.read_csv(dataset)
print(dataset.shape)

# define predictors and target
pred   = model_config['meta']['predictors']
target = model_config['meta']['target']

X = dataset[pred]
y = dataset[target]

print('X Shape:', X.shape)
print('y Shape:', y.shape)

# Define an objective function
def main():
    # Enable autolog()
    # mlflow.sklearn.autolog() requires mlflow 1.11.0 or above.
    mlflow.sklearn.autolog()

#Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y,
                                                    test_size=model_config['parameter']['test_size'], random_state=42)
print('X_train, X_test, y_train, y_test shapes:', X_train.shape, X_test.shape, y_train.shape, y_test.shape)

#print("size of full dataset = ", len(data))
print("size of training dataset = ", len(X_train))
print("size of test dataset = ", len(X_test))

#Scaling the features
# Scale these features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.fit_transform(X_test)

X_train_scaled
print("Scaling...")


#Defining the model
model = LinearRegression()
model

#Logging metrics with mlflow
with mlflow.start_run(run_name = model_config['meta']['run_name']) as run:
    mlflow.set_tag('remark', model_config['meta']['tag'])

    #Fitting the Model
    model.fit(X_train_scaled, y_train) #Change to X_Train?
    print('Fitting...')


    # Run the 3-fold cross validation
    scores = cross_val_score(
        model,
        X_train_scaled,
        y_train,
        cv=model_config['parameter']['outer_cv'],
    )

    # Report
    print('Cross validation scores on training:')
    print("R^2 scores = ", scores)
    print("Scores mean = ", scores.mean())
    print("Score std dev = ", scores.std())


    #Creating predictions
    y_pred = model.predict(X_test_scaled)
    print(y_pred.describe())
    print(y_test.describe())

    #TEst Scores
    print('Test Metrics:')
    print("MAE", mean_absolute_error(y_test, y_pred))
    print("R2", r2_score(y_test, y_pred))

    log_model(model, 'model')
    mlflow.log_metric("MAE", mean_absolute_error(y_test, y_pred))
    mlflow.log_metric("MSE", mean_squared_error(y_test, y_pred, squared=True))
    mlflow.log_metric("RMSE", mean_squared_error(y_test, y_pred, squared=False))
    mlflow.log_metric("R2", r2_score(y_test, y_pred))
    mlflow.log_metric("MAPE", 100*np.mean(abs(y_pred - y_test)/ y_test))
# Perhaps also have Adjusted R2 ?


if __name__ == "__main__":
    main()

mlflow.end_run()

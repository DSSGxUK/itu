# load libraries
import yaml
import pandas as pd
import plotly.figure_factory as ff
import mlflow
import numpy as np
import plotly.express as px
import subprocess

from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV, GridSearchCV
from sklearn.svm import SVR
from sklearn.metrics import make_scorer
from datetime import datetime, date

# save runs
mlflow.set_tracking_uri("file:///files/mlruns")
mlflow.tracking.get_tracking_uri()

#Implementing start time
begin_time = datetime.now()
print("#####################################################")
print("Run Start:",begin_time)
print("#####################################################")

# read in (yaml) configs
with open('../../conf/model_config.yaml', 'r') as conf:
    model_config = yaml.safe_load(conf)

print("#####################################################")
print("Model config file loaded")
print("#####################################################")

#Mlflow VERSION
print("MLflow Version:",mlflow.version.VERSION)
print("MLflow Tracking URI:", mlflow.get_tracking_uri())

#Naming the set_experiment
dt = date.today().strftime('%d/%m/%Y')
experiment_name= dt + model_config['meta']['experiment_name']

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

# create inner and outer cross-validation sets
inner_cv = KFold(n_splits = model_config['parameter']['inner_cv'], shuffle=True)

# define parameter grid
parameters = {'C': model_config['parameter']['svm']['C'], 'gamma': model_config['parameter']['svm']['gamma'],
'kernel': model_config['parameter']['svm']['kernel']}

# define model class to use
model = SVR()

#Create custom scoring
def custom_eval_metric(y_true, y_pred):
    #errors_low_ytest = abs(y_pred[np.asarray(y_true).flatten()<0.3] - np.asarray(y_true[np.asarray(y_true).flatten()<0.3]).flatten())
    errors_low = abs(y_pred[y_pred<model_config['parameter']['threshold']] - np.asarray(y_true[y_pred<model_config['parameter']['threshold']]).flatten())
    return np.mean(errors_low)

custom_scorer = make_scorer(custom_eval_metric, greater_is_better = False)

# define grid search
search = GridSearchCV(model, parameters, scoring = custom_scorer, cv = inner_cv ,
                            refit=True,
                            verbose = 2)

print("#####################################################")
print('start tuning')
print("#####################################################")

# find best parameters
result = search.fit(X_train, y_train)

print("#####################################################")
print("finished tuning")
print("#####################################################")

#for i in range(len(search.cv_results_['mean_fit_time'])):
#    with mlflow.start_run():
#        mlflow.log_metric("mean test score", search.cv_results_['mean_test_score'][i])
#        mlflow.log_param('C', search.cv_results_['params'][i]['C'])
#        mlflow.log_param('kernel', search.cv_results_['params'][i]['kernel'])
#        mlflow.log_param('gamma', search.cv_results_['params'][i]['gamma'])
#    mlflow.end_run()

best_parameter = search.best_params_

print("#####################################################")
print(best_parameter)
print("#####################################################")

# define model class to use
model = SVR(C=best_parameter['C'], kernel=best_parameter['kernel'],
                              gamma=best_parameter['gamma'])

# find best parameters
model.fit(X_train, y_train)

# predict holdout set
pred = model.predict(X_test)

# Absolute error
errors = abs(pred - y_test.iloc[:,0].to_numpy())
avg_error = np.mean(errors)

#Low tail error
errors_low_pred = abs(pred[pred<model_config['parameter']['threshold']] - np.asarray(y_test[pred<model_config['parameter']['threshold']]).flatten())

#Low tail error
errors_low_truth = abs(pred[np.asarray(y_test).flatten()<model_config['parameter']['threshold']] - np.asarray(y_test[np.asarray(y_test).flatten()<model_config['parameter']['threshold']]).flatten())

#avg error for pred below .3
avg_error_low_pred = np.mean(errors_low_pred)
#avg error for GT below .3
avg_error_low_truth = np.mean(errors_low_truth)

#standard deviation for pred below .3
stan_dev_low_pred = np.std(errors_low_pred)
#standard deviation for GT below .3
stan_dev_low_truth = np.std(errors_low_truth)

print("#####################################################")
print('avg error: ', round(avg_error, 2))
print('Just the lower errors: ', np.round(errors_low_pred,2 ))
print('Schools pred below .3:' , len(pred[pred<model_config['parameter']['threshold']]))
print('Mean lower pred error: ', round(avg_error_low_pred, 2))
print('GT School below .3:' , len(y_test[y_test['target']<model_config['parameter']['threshold']]))
print('Mean lower ground truth error: ', round(avg_error_low_truth, 2))
print('Standard Dev of Low Error: ', round(stan_dev_low_pred, 2))
print("#####################################################")

#This creates a text file in data/interim folder that saves the predictors used in this experiment
with open("../../data/interim/predictors.txt", "w") as f:
    f.write(str(model_config['meta']['predictors']))

#This creates a text file in data/interim folder that saves the dependencies
with open('../../data/interim/requirements.txt', 'w') as f:
    process = subprocess.Popen(['pip', 'freeze'], stdout=f)

# log metrics of winning model
with mlflow.start_run(run_name = model_config['meta']['run_name']) as run:
    mlflow.log_metric("avg error", avg_error)
    mlflow.log_metric("low avg error", avg_error_low_pred)
    mlflow.log_metric('low gt avg error', avg_error_low_truth)
    mlflow.log_metric("std error", stan_dev_low_pred)
    mlflow.log_param('C', best_parameter['C'])
    mlflow.log_param('kernel', best_parameter['kernel'])
    mlflow.log_param('gamma', best_parameter['gamma'])
    mlflow.sklearn.log_model(model, 'model')
    mlflow.log_artifact("../../data/interim/predictors.txt")
    mlflow.log_artifact('../../data/interim/requirements.txt')
mlflow.end_run()

print("#####################################################")
print("Run Time:", datetime.now() - begin_time)
print("#####################################################")

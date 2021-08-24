# load libraries
import yaml
import mlflow
import pandas as pd
import numpy as np

from mlflow.sklearn import log_model
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV, GridSearchCV
from sklearn.metrics import make_scorer
from datetime import datetime, date
import subprocess

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
dataset = model_config['model']['loc'] + model_config['model']['file']
dataset = pd.read_csv(dataset)
# subset for faster trial and error
#dataset = dataset.iloc[0:1000,:]

print("#####################################################")
print("training data loaded")
print("#####################################################")

# define predictors and target
pred   = model_config['meta']['predictors']
target = model_config['meta']['target']

X = dataset[pred]
y = dataset[target]

#Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y,
test_size = model_config['parameter']['test_size'], random_state = 42)

print("#####################################################")
print("size of training dataset = ", len(X_train))
print("size of hold out dataset = ", len(X_test))
print("#####################################################")

# create inner cross-validation sets
inner_cv = KFold(n_splits = model_config['parameter']['inner_cv'], shuffle = True)

# define parameter grid
parameters = {"n_estimators": model_config['parameter']['Random_Forest']['n_estimators'],
"max_depth": model_config['parameter']['Random_Forest']['max_depth']}

# define model class to use
model = RandomForestRegressor(random_state = 42)

#Create custom scoring
def custom_eval_metric(y_true, y_pred):
    #errors_low_ytest = abs(y_pred[np.asarray(y_true).flatten()<0.3] - np.asarray(y_true[np.asarray(y_true).flatten()<0.3]).flatten())
    errors_low = abs(y_pred[y_pred<0.3] - np.asarray(y_true[y_pred<0.3]).flatten())
    return np.mean(errors_low)

custom_scorer = make_scorer(custom_eval_metric, greater_is_better = False)

# # define grid search
# search = RandomizedSearchCV(model, parameters, cv = inner_cv, random_state = 42,
# verbose = 2, n_iter = model_config['parameter']['iterations'],
# scoring = custom_scorer)

# define grid search
search = GridSearchCV(model, parameters, scoring = custom_scorer, cv = inner_cv ,
                            refit=True,
                            verbose = 2)

print("#####################################################")
print('start tuning')
print("#####################################################")

# find best parameters
search.fit(X_train, y_train.values.ravel())

print("#####################################################")
print("finished tuning")
print("#####################################################")

print("#####################################################")
print("logging mlfow runs")
print("#####################################################")
#
# for i in range(len(search.cv_results_['mean_fit_time'])):
#     print (100*(i/len(search.cv_results_['mean_fit_time'])), ' % finished')
#     with mlflow.start_run(run_name = model_config['meta']['run_name']) as run:
#         mlflow.log_metric("low error pred", search.cv_results_['mean_test_score'][i])
#         mlflow.log_param('n_estimators', search.cv_results_['params'][i]['n_estimators'])
#         mlflow.log_param('max_depth', search.cv_results_['params'][i]['max_depth'])
#     mlflow.end_run()

# choose best parameter from tuning
best_parameter = search.best_params_

print("#####################################################")
print("choose best parameter from tuning: ", best_parameter)
print("#####################################################")

# train model on winning parameters from training
model = RandomForestRegressor(random_state = 42,
                              n_estimators = best_parameter['n_estimators'],
                              max_depth = best_parameter['max_depth']
                              )
model.fit(X_train, y_train.values.ravel())

# predict holdout set
pred = model.predict(X_test)

# Absolute error
errors = abs(pred - y_test.iloc[:,0].to_numpy())
avg_error = np.mean(errors)

#Focusing on the predictions that are below .3
errors_low_pred = abs(pred[pred < 0.3] - np.asarray(y_test[pred < 0.3]).flatten())

#Focusing on the ground truth that is below .3
errors_low_truth = abs(pred[np.asarray(y_test).flatten() < 0.3] - np.asarray(y_test[np.asarray(y_test).flatten() < 0.3]).flatten())

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
print('Schools pred below .3:' , len(pred[pred<.3]))
print('Mean lower pred error: ', round(avg_error_low_pred, 2))
print('GT School below .3:' , len(y_test[y_test['A4A_right']<0.3]))
print('Mean lower ground truth error: ', round(avg_error_low_truth, 2))
print('Standard Dev of Low Error: ', round(stan_dev_low_pred, 2))
print("#####################################################")

#This creates a text file in data/interim folder that saves the predictors used in this experiment
with open("../../data/interim/predictors.txt", "w") as f:
    f.write(str(model_config['meta']['predictors']))

#This creates a text file in data/interim folder that saves the predictors used in this experiment
with open('../../data/interim/requirements.txt', 'w') as f:
    process = subprocess.Popen(['pip', 'freeze'], stdout=f)

# log metrics of winning model
with mlflow.start_run(run_name = model_config['meta']['run_name']) as run:
    mlflow.log_metric("avg error", avg_error)
    mlflow.log_metric("low avg error", avg_error_low_pred)
    mlflow.log_metric('low gt avg error', avg_error_low_truth)
    mlflow.log_metric("std error", stan_dev_low_pred)
    mlflow.log_param('n_estimators', best_parameter['n_estimators'])
    mlflow.log_param('max_depth', best_parameter['max_depth'])
    mlflow.sklearn.log_model(model, 'model')
    mlflow.log_artifact("../../data/interim/predictors.txt")
    mlflow.log_artifact('../../data/interim/requirements.txt')
    #mlflow.log_artifact('var_imp_plot.png')
mlflow.end_run()

print("#####################################################")
print("Run Time:", datetime.now() - begin_time)
print("#####################################################")

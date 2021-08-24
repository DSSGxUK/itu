# load libraries
import yaml
import lightgbm
import pandas as pd
import plotly.figure_factory as ff
import mlflow
import numpy as np

from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV
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
dataset = model_config['model']['loc'] + model_config['model']['file']
dataset = pd.read_csv(dataset)
# subset for faster trial and error
#dataset = dataset.iloc[0:1000,:]

print("#####################################################")
print("training data loaded")
print("#####################################################")

# define predictors and target
pred   = ['avg_d_kbps', 'mean_GHM', 'avg_rad_mean', 'viirs_yr', 'ghsl_mean', '19_cf_cvg_mean']
target = ['A4A_right']

X = dataset[pred]
y = dataset[target]

print("#####################################################")
print('X Shape:', X.shape)
print('y Shape:', y.shape)
print("#######data_dmatrix = xgb.DMatrix(data=X,label=y)##############################################")

#Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = model_config['parameter']['test_size'],
                                                    random_state = 42)

print("#####################################################")
print('X_train, X_test, y_train, y_test shapes:', X_train.shape, X_test.shape, y_train.shape, y_test.shape)
print("size of training dataset = ", len(X_train))
print("size of test dataset = ", len(X_test))
print("#####################################################")

# create inner and outer cross-validation sets
inner_cv = KFold(n_splits = model_config['parameter']['inner_cv'], shuffle=True)

# define parameter grid
parameters = {"boosting_type": model_config['parameter']['lightgbm']['boosting_type'],"max_depth": model_config['parameter']['lightgbm']['max_depth'],
              "learning_rate": model_config['parameter']['lightgbm']['learning_rate']],
              "n_estimators": model_config['parameter']['lightgbm']['n_estimators']}

# define model class to use
model = lightgbm.LGBMRegressor(random_state = 42, objective = 'regression_l1')

# define grid search
search = RandomizedSearchCV(model, parameters, cv = inner_cv, random_state = 42,
verbose = 2, n_iter = model_config['parameter']['iterations'])

print("#####################################################")
print('start tuning')
print("#####################################################")

# find best parameters
search.fit(X_train, y_train)

print("#####################################################")
print("finished tuning")
print("#####################################################")

for i in range(model_config['parameter']['iterations']):
    with mlflow.start_run():
        mlflow.log_metric("mean test score", search.cv_results_['mean_test_score'][i])
        mlflow.log_param('n_estimators', search.cv_results_['params'][i]['n_estimators'])
        mlflow.log_param('max_depth', search.cv_results_['params'][i]['max_depth'])
        mlflow.log_param('learning_rate', search.cv_results_['params'][i]['learning_rate'])
        mlflow.log_param('boosting_type', search.cv_results_['params'][i]['boosting_type'])
    mlflow.end_run()

best_parameter = search.best_params_
print("#####################################################")
print(best_parameter)
print("#####################################################")

# define model class to use
model = lightgbm.LGBMRegressor(random_state = 42, boosting_type = best_parameter['boosting_type'],
                              n_estimators = best_parameter['n_estimators'],
                              max_depth = best_parameter['max_depth'],
                              learning_rate = best_parameter['learning_rate'])

# find best parameters
model.fit(X_train, y_train)

# predict holdout set
pred = search.predict(X_test)

# Absolute error
errors = abs(pred - y_test.iloc[:,0].to_numpy())
avg_error = np.mean(errors)

print("#####################################################")
print(avg_error)
print("#####################################################")

online_pop = [pred, y_test.iloc[:,0].to_numpy()]
labels = ['predictions', 'reality']

fig = ff.create_distplot(online_pop, labels, show_hist = False)
#fig.write_image('comp_plot.png')
imp_plt = lightgbm.plot_importance(model)
#imp_plt.savefig('var_imp_plot.png')

with mlflow.start_run():
    mlflow.log_metric("holdout score", avg_error)
    mlflow.log_param('n_estimators', best_parameter['n_estimators'])
    mlflow.log_param('max_depth', best_parameter['max_depth'])
    mlflow.log_param('learning_rate', best_parameter['learning_rate'])
    mlflow.log_param('boosting_type', best_parameter['boosting_type'])
    mlflow.sklearn.log_model(model, 'model')
    #mlflow.log_artifact('comp_plot.png')
    #mlflow.log_artifact('var_imp_plot.png')
mlflow.end_run()

print("#####################################################")
print("Run Time:", datetime.now() - begin_time)
print("#####################################################")

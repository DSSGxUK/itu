# load libraries
import yaml
import pandas as pd
import plotly.figure_factory as ff
import mlflow
import numpy as np

from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV
from sklearn.svm import SVR
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
pred   = model_config['meta']['predictors']
target = model_config['meta']['target']

X = dataset[pred]
y = dataset[target]

print("#####################################################")
print('X Shape:', X.shape)
print('y Shape:', y.shape)
print("#####################################################")

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
parameters = {'C': model_config['parameter']['svm']['C'], 'gamma': model_config['parameter']['svm']['gamma'],
'kernel': model_config['parameter']['svm']['kernel']}

# define model class to use
model = SVR()

# define grid search
search = RandomizedSearchCV(model, parameters, cv=inner_cv, random_state=42,
                            verbose=2, n_iter=model_config['parameter']['iterations'])

print("#####################################################")
print('start tuning')
print("#####################################################")

# find best parameters
search.fit(X_train, y_train)

print("#####################################################")
print("finished tuning")
print("#####################################################")

for i in range(6):
    with mlflow.start_run():
        mlflow.log_metric("mean test score", search.cv_results_['mean_test_score'][i])
        mlflow.log_param('C', search.cv_results_['params'][i]['C'])
        mlflow.log_param('kernel', search.cv_results_['params'][i]['kernel'])
        mlflow.log_param('gamma', search.cv_results_['params'][i]['gamma'])
    mlflow.end_run()

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
pred = search.predict(X_test)

# Absolute error
errors = abs(pred - y_test.iloc[:,0].to_numpy())
avg_error = np.mean(errors)

print("#####################################################")
print(avg_error)
print("#####################################################")

online_pop = [pred, y_test.iloc[:,0].to_numpy()]
labels = ['predictions', 'reality']

#fig = ff.create_distplot(online_pop, labels, show_hist = False)
y = y_test.iloc[:,0].to_numpy()
y_pred = pred

fig = px.scatter(x=y, y=y_pred, labels={'x': 'ground truth', 'y': 'prediction'},
                 title = 'Comparison between predictions and reality',
                 template = 'plotly_dark')
fig.update_traces(marker=dict(size=3,
                              color=((abs(y-y_pred) < 0.15).astype('int')),
                              colorscale=[[0, '#FAED27'],[1, '#98FB98']])
                             )
fig.add_shape(
    type="line", line=dict(dash='dash'),
    x0=y.min(), y0=y.min(),
    x1=y.max(), y1=y.max()
)
fig.show()
#fig.write_image('comp_plot.png')
#imp_plt = lightgbm.plot_importance(model)
#imp_plt.savefig('var_imp_plot.png')

with mlflow.start_run():
    mlflow.log_metric("holdout score", avg_error)
    mlflow.log_param('C', best_parameter['C'])
    mlflow.log_param('kernel', best_parameter['kernel'])
    mlflow.log_param('gamma', best_parameter['gamma'])
    mlflow.sklearn.log_model(model, 'model')
    #mlflow.log_artifact('comp_plot.png')
    #mlflow.log_artifact('var_imp_plot.png')
mlflow.end_run()

print("#####################################################")
print("Run Time:", datetime.now() - begin_time)
print("#####################################################")

# load libraries
import yaml
import pandas as pd
import plotly.figure_factory as ff
import mlflow
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import plotly.express as px
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, KFold, RandomizedSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, r2_score
from torch.utils.data import Dataset, DataLoader
from datetime import datetime, date
from tqdm.notebook import tqdm
from sklearn import datasets
from sklearn.datasets import load_diabetes

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

# #Mlflow VERSION
# print("MLflow Version:",mlflow.version.VERSION)
# print("MLflow Tracking URI:", mlflow.get_tracking_uri())
#
# #Naming the set_experiment
# dt = date.today().strftime('%d/%m/%Y')
# experiment_name= dt + model_config['meta']['experiment_name']
#
# mlflow.set_experiment(experiment_name)
# mlflow_client = mlflow.tracking.MlflowClient()
# experiment_id = mlflow_client.get_experiment_by_name(experiment_name).experiment_id
#
# print("#####################################################")
# print("Experiment_id:",experiment_id)
# print("Experiment_name:", experiment_name)
# print("#####################################################")

# import data
dataset = model_config['model']['loc'] + model_config['model']['file']
dataset = pd.read_csv(dataset)

# subset for faster trial and error
# dataset = dataset.iloc[0:1000,:]

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

# Train-test split
X_trainval, X_test, y_trainval, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# Train-val split
X_train, X_val, y_train, y_val = train_test_split(X_trainval, y_trainval,
                                                  test_size=0.1, random_state=42)

print("#####################################################")
print('X_train, X_val, X_test, y_train, y_val, y_test shapes:',
      X_train.shape, X_val.shape, X_test.shape, y_train.shape, y_val.shape, y_test.shape)
print("size of training dataset = ", len(X_train))
print("size of validation dataset = ", len(X_val))
print("size of test dataset = ", len(X_test))
print("#####################################################")

# scale and format data
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_val = scaler.transform(X_val)
X_test = scaler.transform(X_test)
X_train, y_train = np.array(X_train), np.array(y_train)
X_val, y_val = np.array(X_val), np.array(y_val)
X_test, y_test = np.array(X_test), np.array(y_test)
y_train, y_test, y_val = y_train.astype(float), y_test.astype(float), y_val.astype(float)

# create inner and outer cross-validation sets
#inner_cv = KFold(n_splits=model_config['parameter']['inner_cv'], shuffle=True)

# create model class
class MultipleRegression(nn.Module):
    def __init__(self, num_features):
        super(MultipleRegression, self).__init__()

        self.layer_1 = nn.Linear(num_features, 16)
        self.layer_2 = nn.Linear(16, 32)
        self.layer_3 = nn.Linear(32, 16)
        self.layer_out = nn.Linear(16, 1)
        self.relu = nn.ReLU()

    def forward(self, inputs):
        x = self.relu(self.layer_1(inputs))
        x = self.relu(self.layer_2(x))
        x = self.relu(self.layer_3(x))
        x = self.layer_out(x)

        return (x)

    def predict(self, test_inputs):
        x = self.relu(self.layer_1(test_inputs))
        x = self.relu(self.layer_2(x))
        x = self.relu(self.layer_3(x))
        x = self.layer_out(x)

        return (x)

# generate model-ready dataset
class RegressionDataset(Dataset):

    def __init__(self, X_data, y_data):
        self.X_data = X_data
        self.y_data = y_data

    def __getitem__(self, index):
        return self.X_data[index], self.y_data[index]

    def __len__ (self):
        return len(self.X_data)

# get model-ready datasets
train_dataset = RegressionDataset(torch.from_numpy(X_train).float(), torch.from_numpy(y_train).float())
val_dataset = RegressionDataset(torch.from_numpy(X_val).float(), torch.from_numpy(y_val).float())
test_dataset = RegressionDataset(torch.from_numpy(X_test).float(), torch.from_numpy(y_test).float())

# parameters
EPOCHS = 50
BATCH_SIZE = 32
LEARNING_RATE = 0.001
NUM_FEATURES = len(X.columns)

# define data loaders
train_loader = DataLoader(dataset=train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(dataset=val_dataset, batch_size=1)
test_loader = DataLoader(dataset=test_dataset, batch_size=1)

# set device
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

# define model class to use
model = MultipleRegression(NUM_FEATURES)
model.to(device)
print('#####################################################')
print('Model = ', model)
print('#####################################################')
#criterion = nn.L1Loss()
def criterion(pred, truth):
    errors_low_pred = abs(pred[pred < 0.3] - (truth[pred < 0.3]).flatten())

    return errors_low_pred

optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

print("#####################################################")
print('start training')
print("#####################################################")

loss_stats = {'train': [], "val": []}

for e in tqdm(range(1, EPOCHS+1)):
    # TRAINING
    train_epoch_loss = 0

    model.train()
    for X_train_batch, y_train_batch in train_loader:
        X_train_batch, y_train_batch = X_train_batch.to(device), y_train_batch.to(device)
        optimizer.zero_grad()

        y_train_pred = model(X_train_batch)

        train_loss = criterion(y_train_pred, y_train_batch.unsqueeze(1))
        train_loss = train_loss.sum()
        train_loss.backward()
        optimizer.step()

        train_epoch_loss += train_loss.item()

    # VALIDATION
    with torch.no_grad():
        val_epoch_loss = 0

        model.eval()
        for X_val_batch, y_val_batch in val_loader:
            X_val_batch, y_val_batch = X_val_batch.to(device), y_val_batch.to(device)

            y_val_pred = model(X_val_batch)

            val_loss = criterion(y_val_pred, y_val_batch.unsqueeze(1))
            val_loss = val_loss.sum()

            val_epoch_loss += val_loss.item()

    loss_stats['train'].append(train_epoch_loss/len(train_loader))
    loss_stats['val'].append(val_epoch_loss/len(val_loader))

    print(f'Epoch {e+0:03}: | Train Loss: {train_epoch_loss/len(train_loader):.5f} | Val Loss: {val_epoch_loss/len(val_loader):.5f}')

print("#####################################################")
print("finished training")
print("#####################################################")

y_pred_list = []
with torch.no_grad():
    model.eval()
    for X_batch, _ in test_loader:
        X_batch = X_batch.to(device)
        y_test_pred = model(X_batch)
        y_pred_list.append(y_test_pred.cpu().numpy())

y_pred = y_pred_list
y_pred_list = [a.squeeze().tolist() for a in y_pred_list]


#errors_low_pred = abs(y_pred[y_pred < 0.3] - np.asarray(y_test[y_pred < 0.3]).flatten())
# Absolute error
errors = abs(y_pred_list - y_test)
avg_error = np.mean(errors)
#avg_low_error = np.mean(erros_low_pred)

print("#####################################################")
print(avg_error)
print("#####################################################")

online_pop = [y_pred_list, y_test]
labels = ['predictions', 'reality']

plt.scatter(y_test, y_pred_list)
plt.show()
mae = mean_absolute_error(y_test, y_pred_list)
r_square = r2_score(y_test, y_pred_list)
print("Mean Absolute Error :",mae)
print("R^2 :",r_square)

# with mlflow.start_run():
#     mlflow.log_metric("holdout score", avg_error)
#     mlflow.sklearn.log_model(model, 'model')
#     #mlflow.log_artifact('comp_plot.png')
#     #mlflow.log_artifact('var_imp_plot.png')
# mlflow.end_run()

print("#####################################################")
print("Run Time:", datetime.now() - begin_time)
print("#####################################################")
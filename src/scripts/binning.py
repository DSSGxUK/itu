import os, sys, stat
import pandas as pd

# read latest regression training dataset for country
data = pd.read_csv('../../data/training_sets/Brazil/training_set_v001.csv')

# convert target variable to string
data = data.astype({'target': 'str'})
# iterate over training dataset rows
for row in data.itertuples():
    # assign target variable 0 if it is less than or equal to 0.3 and 1 otherwise
    if float(row.target) <= 0.3:
        data.at[row[0], 'target'] = 0
    else:
        data.at[row[0], 'target'] = 1

# save binned training dataset for classification
with open('../../data/training_sets/Brazil/training_set_v001_binned.csv', 'w') as out:
    data.to_csv(out)
    os.chmod('../../data/training_sets/Brazil/training_set_v001_binned.csv', stat.S_IRWXO)
out.close()
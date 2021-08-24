<!-- load mermaid -->

<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>

<script>

mermaid.initialize({startOnLoad:true});

mermaidAPI.initialize({

securityLevel: 'loose'

});

</script>

# Feature Engineering

Having retrieved data of many different types, at different geospatial resolutions, from an array of different sources, it was necessary to develop a robust and comprehensive feature engineering pipeline, which produces clean datasets, ready for model training or application.

## Data Cleaning

* `Numerical Variables` - Impute missing values as variable median.
* `Categorical Variables` - Fill missing values with 'missing' label; perform one-hot encoding.

## Target Variable

Our target variable is ground-truth survey data on local internet connectivity. For the Brazilian and Thai surveys, forwarded to us by ITU, these target variables correspond to the following labels:

* `Brazil` - A4A
* `Thailand` - H107

In each case, we rename our target variable to simply 'target'.

## Joining Locations

In the following description, we use the word 'feature' to mean predictor and, in some cases, ground truth survey variable. The map_feature method within the FeatureEngineering class is used to perform a spatial join between school locations and feature values. In essence, we are finding the correct value of each feature at each given school location. To do so, we first ensure that the dataframe corresponding to each predictor or survey dataset is loaded as a geodataframe, with an appropriately defined 'geometry' column. If the feature's geometry is a polygon, or multipolygon, rather than a point, we take the centroid as the location with which to match. If, instead, the feature's geometry is defined by latitude and longitude columns, rather than a single geometry column, this will be handled appropriately, so long as these column names are exactly 'latitude' and 'longitude', or 'lat' and 'lon'.

For the unexpected instance in which schools have already been matched to feature values, we look for a 'source_school_id' column and merge the school data to the feature data according to these school ids. This is for the sake of code robustness, in case features that are already mapped to schools are mistakenly passed to the map_feature method.

The build_tree method is then called to implement Scikit-learn's KDTree package and thus build a kd tree of the previously defined centroids. The kd tree is a tree in k-dimensional space; for us, this defines the spatial relationships between locations. This tree is then queried with the school locations to get the nearest neighbours, with the query returning dist (geographic distance) and ind (index associated with this location). The rows in the school_data dataframe are then assigned the correct values for each new column. For any variable named 'range', such as the mobile cell tower range variable from the OpenCellID dataset, values are converted to a 0 or 1, corresponding to range < dist and range >= dist respectively. This last part converts any 'range' to a binary variable, representing out-of-range, or in-range.

### If Dataset Is Sparsely Scattered across Country:
It should be noted that the map_feature method should only be used for features that are not sparsely distributed. For example, this method is not used for the Brazil survey data, which is only available for a selection of enumeration areas, which often have significant geographic regions between them.

For other features, such as the Brazil survey data, which have values only in sparsely distributed locations, we employ the map_enumeration method, which joins school locations to areas via intersections between the enumeration area polygons and 1km radius school buffer zones. We then check for instances in which a school might have been joined to multiple enumeration areas and select only the nearest enumeration area for such cases.

## High Level Feature Engineering Pipeline 

<div class='mermaid'>
graph TD
  A[Get School Data] --> B{Is Survey Available?};
  B --> |Yes| C[Get Survey Data];
  B --> |No| D[Load Predictor Dataset];
  C --> E
  D --> E[Initialise New Columns];
  E --> F[Clean New Data];
  F --> G[Match New Data to Schools];
  G --> H{All Features Added?};
  H --> |Yes| I[Save Dataset]
  H --> |No| D;
</div>

## Classification Use Case

Our problem is a regression problem, with an outcome that needs to be predictions from 0 -1. However, should you wish to train or apply a classifier, instead of a regression model, you can create a binary classification dataset by running the 'binning.py' script, found in the src/scripts/ folder. Within this script, it is straightforward to edit the name of a standard regression training dataset that you wish to convert into a classification-ready dataset. To train/apply a classification model, one would then simply need to change the dataset file name within the 'configs.yml' file.

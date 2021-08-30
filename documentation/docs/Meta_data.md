# Meta Data Information

## Folder Structure
Below is the folder structure for the Github Repository. All of the notebooks and scripts are organized within the below folder structure and data is inputted with relative file paths. Therefore, once you set your own working directory, everything within should run on its own. 

- conf/
- data/
  - geodata/
  - meta/
  - school_loc/
  - fb/
  - opencellid/
  - satellite/
  - speedtest/
  - survey/
    - Brazil/
    - Thailand/
    - Philippines/
  - training_sets/
    - Brazil/
    - Thailand/
    - Philippines/
  - worldpop/
- model/
- notebooks/
- src/
  - scripts/
    - map_offline
      - data_gathering
        - __init__.py
        - opendata.py
        - opendata_utils.py
        - opendata_scrap.py
        - opendata_facebook.py
        - opendata_satellite.py
      - feature_engineering
        - __init__.py
        - data_pipeline.py
        - configs.py
      - country.py
      - survey.py
      - school.py
      - main.py
- requirements.txt

## Configurations

We use configs.py to store the variable configurations that should be changed according to use-case:

* `WD` - Working Directory, e.g. 'C:/Users/itu/DSSGx/'
* `COUNTRY` - Country name for current use-case, e.g. 'Thailand'
* `COUNTRY_CODE` - Country code for current use-case, e.g. 'tha'
* `AVAILABLE_COUNTRIES` - Countries for which survey data with an internet connectivity ground truth variable is available, e.g. list('bra', 'tha')
* `FEATURES` - List of predictive features for use-case, e.g. list('speedtest', 'opencell', 'facebook', 'population', 'satellite'). This exemplary list contains each of the five open data sources we have used and they must be sytactically entered as shown.
* `SCHOOL_BUFFER` - Buffer to define school area which will be used to joining survey and population data to schools, in kilometers
* `SURVEY_AREAS` - Survey dataset geometry join type, 'tiles' if survey will be joined to country administrative region, province, etc., 'enumeration'  if survey will be joined to enumeration area geometries
* `SATELLITE_COLLECTIONS` - Dictionary that has satellite image collection identifier as a key and image collection band names for multi-band images, e.g. '{'MODIS/006/MOD13A2': ['NDVI']}'
* `SATELITTE_START_YEAR` - Start year of satellite imagery collection to be used
* `SATELITTE_END_YEAR` - End year of satellite imagery collection to be used
* `SATELITTE_BUFFER` - Buffer to define school area for which satellite imagery will be collected, in kilometers
* `SATELITTE_MAX_CALL_SIZE` - Google Earth Engine API max feature collection length, by default 5000 points
* `SATELLITE_IMAGE_SCALE` - Satellite Imagery scale of at which to request inputs to a computation is determined from the output. Resolution in meters; used 30 as default in our applications
* `GOOGLE_SERVICES_ACCOUNT` - Google Services Account to call Google Earth Engine API
* `GOOGLE_EARTH_ENGINE_API_JSON_KEY` - JSON key file name that is located under satellite folder
* `OPENCELLID_ACCESS_TOKEN` - OpenCelliD Project API access token as string
* `FACEBOOK_MARKETING_API_ACCESS_TOKEN` - Facebook Marketing API access token as string
* `FACEBOOK_AD_ACCOUNT_ID` - Facebook Ad account id as string
* `FACEBOOK_CALL_LIMIT` -  Facebook Ads Management API maximum calls within one hour, by default it is 300 + 40 * (Number of Active Ads)
* `FACEBOOK_RADIUS` - Radius to define school area for which Facebook API data will be collected, in kilometers
* `FACEBOOK_SCHOOL_DATA_LEN` - # of schools in the dataset to keep facebook data with school length in the name in case schools wanted to be divided into chunks and also approximate Facebook API completion time
* `SPEEDTEST_TILE_TYPE` - Service type for Ookla Open Speedtest Dataset can be 'fixed' or 'mobile' representing fixed or mobile network performance aggregates of tiles
* `SPEEDTEST_TILE_YEAR` - Speedtest data year, e.g. 2021
* `SPEEDTEST_TILE_QUARTER` - Speedtest data quarter, e.g. 2
* `POPULATION_DATASET_YEAR` - Population counts dataset year

## Data Dictionaries

Data dictionaries should be created for each predictor and survey dataset. Dictionaries for the open-source data and Brazilian, Thai and Philippino survey data already exist and should be located in the data/meta/ folder.

An exemplary data dictionary (for speedtest data) is shown below:

| Number      | Name      | Description                        | Type     | Binary     | Role         | Use     | Comment               |
| ----------- | ---------- | ----------------------------------- | ----------- | ----------- | --------------- | ----------- | ----------------------- |
| 1       | `avg_d_kbps` | The average download speed of all tests performed in the tile, represented in kilobits per second | num | N | predictor | Y | mbps can also be used |
| 2       | `avg_u_kbps` | The average upload speed of all tests performed in the tile, represented in kilobits per second | num | N | predictor | Y | mbps can also be used |
| 3       | `avg_lat_ms` | The average latency of all tests performed in the tile, represented in milliseconds | num | N | predictor | N | |
| 4       | `tests` | The number of tests taken in the tile | num | N | predictor | N | |
| 5       | `devices` | The number of unique devices contributing tests in the tile | num | N | predictor | N | |
# Configurations

We use configs.py to store the variable configurations that should be changed according to use-case:

* `WD` - Working Directory, e.g. 'C:/Users/itu/DSSGx/'
* `COUNTRY` - Country name for current use-case, e.g. 'Thailand'
* `COUNTRY_CODE` - Country code for current use-case, e.g. 'tha'
* `AVAILABLE_COUNTRIES` - Countries for which survey data with an internet connectivity ground truth variable is available, e.g. list('bra', 'tha')
* `FEATURES` - List of predictive features for use-case, e.g. list('speedtest', 'opencell', 'facebook', 'population', 'satellite'). This exemplary list contains each of the five open data sources we have used and they must be sytactically entered as shown.
* `SURVEY_AREAS` - Survey dataset geometry join type, 'tiles' if survey will be joined to country administrative region, province, etc., 'enumeration'  if survey will be joined to enumeration area geometries
* `SATELLITE_COLLECTIONS` - Dictionary that has satellite image collection identifier as a key and image collection band names for multi-band images, e.g. '{'MODIS/006/MOD13A2': ['NDVI']}'
* `SATELITTE_START_YEAR` - Start year of satellite imagery collection to be used
* `SATELITTE_END_YEAR` - End year of satellite imagery collection to be used
* `SATELITTE_BUFFER` - Buffer to define school area for which satellite imagery will be collected, in kilometers
* `SATELITTE_MAX_CALL_SIZE` - Google Earth Engine API max feature collection length, by default 5000 points
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
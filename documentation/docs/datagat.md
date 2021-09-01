<!-- load mermaid -->

<script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>

<script>

mermaid.initialize({startOnLoad:true});

mermaidAPI.initialize({

securityLevel: 'loose'

});

</script>

# Data Gathering

## Getting Started

### Instructions to Create Model-Ready Dataset

1. Create a Conda virtual environment with all the packages installed by following the directions below. A note that if you have a mac, some of the packages like GDAL might be harder to install.
    - Make sure you have the miniconda shell or another type of terminal installed. Type `conda info --envs` to see the other environments that exist and to verify you are in the base environment.
    - Then type `conda env create tovaperlman/itu_test_02` . It should take a few moments to minutes for all the packages to download.
    - Once this is done, you can check that it's an environment present in your computer by typing again `conda info --envs`
    - Then to activate the environment you can type `conda activate itu_test_02`

2. Once you've activated the environment which has all the necessary packages and dependencies installed, navigate in the same terminal to wherever you've saved the repository. Within that navigate to src/scripts/map_offline/. Then open the repository within a code editor (Visual Studio Code, Atom, Pycharm, etc.)

3. To generate a dataframe comprising any target variables and predictors that you wish to use, first set up the use case configurations in feature_engineering/configs.py. Details of the configurable variables and their expected assignments can be found in the 'Meta Data Information/ configurations' section of the documentation.

4. To fully set up the configurations, you must separately get access tokens for OpenCelliD Project, Google Earth Engine API, and Facebook Marketing API. Once you have these, log all of them in the configs file. Otherwise, you will get errors when trying to run the scripts.
    - For [Open Cell ID](https://opencellid.org/), you just need to sign up for an account and it will give you an API Access Token.
    - For **Google Earth Engine**, you must first [sign up](https://signup.earthengine.google.com/) for a [Google Earth Engine account](https://earthengine.google.com/). You cannot use Google Earth Engine unless your application has been approved. Once you receive the application approval email, you can log in to the Earth Engine Code Editor to get familiar with the JavaScript API. Then, follow the steps described below:

        1. To authenticate, you will need to have a Google Cloud Project and enable the Earth Engine API for that project.

        2. Assuming that you are already registered to Earth engine, if it's not the case follow [this link](https://signup.earthengine.google.com/).

        3. First create a cloud project by going [this address](https://console.cloud.google.com/projectcreate/).

        4. Then enable your Earth Engine account in your cloud project from [this link](https://console.cloud.google.com/apis/library/earthengine.googleapis.com).

        5. You can manage the service accounts for your Cloud project by going to the Cloud Console menu (this is the hamburger menu on the side) and selecting IAM & Admin. Once you’ve selected this, select Service accounts on the side. (Choose the project if prompted.)

        6. To create a new service account, click the `CREATE SERVICE ACCOUNT` link. Set service account name and then press done. Then you will see an email that ends with iam.gserviceaccount.com. Copy this whole email and paste it to the configs file next to Google Services Account. Also use [this page](https://signup.earthengine.google.com/#!/service_accounts) to register your service account for use with the Earth Engine API.

        7. Once you have a service account, click the three dots under Actions for that account, then click Manage keys. On that page click the button Add Key and then Create New Key. Choose the JSON. Download the JSON key file. Now add the JSON Key File (which should be in your downloads folder to the data/satellite folder in your directory. Then go to the configs file (in your code editor) and copy and paste the file name of the json file into the GOOGLE_EARTH_ENGINE_API_JSON_KEY.

        8. Well done! You are ready to gather satellite data.
  
    - For **Facebook Marketing API** Access Token, follow the directions from the World Bank [here](https://worldbank.github.io/connectivity_mapping/facebook_nbs/getting_your_token.html).

5. Having correctly set the desired configurations, all you need to do is run 'main.py'. Following this, a dataset for model training and/or application will be saved within a training_sets folder, which is situated within the data directory.

## Internal Data

1. Surveys from ITU for Brazil and Thailand </br></br>
    The target variable for our modeling was the proportion of a population around a particular school that was connected to the internet. It therefore ranged from 0-1, with 0 being zero percent connected and 100 being 100% connected to the internet. We chose to measure this on a school level as one of our objectives, through working with UNICEF, was to detect schools that could be connected to the internet and further serve the community they are located.

    Within the Brazil survey data, we received information on household internet connectivity on an enumeration area level. This presented a slight challenge as the level of granularity of the school data was slightly different from the enumeration data or census tract. Thus, we matched the school points to the enumeration area data. We could not use all the school points as we only had enumeration areas for a specific amount of tracts in Brazil. Thus we had to subset our school points data to around 11,000 points. Once we connected the schools to the enumeration areas we were able to build our training data set. </br></br>

2. School Points from UNICEF for Brazil </br></br>
    We got the school points in lat, long format from UNICEF for Brazil. Unfortunately, we were not able to obtain the school points for Thailand. We turned to OpenStreetMap to obtain school points for Thailand. We obtained many school points but filtered them to the schools that we were positive were schools as some were tagged as dance schools or even ATM's. Our school points script is specific for obtaining the OSM points.

## External/Open Source Data

Brief note on licensing: Most of the data sources we used are open source and for research or educational purposes only and not for commercial use.

[OpenStreetMap®](https://www.openstreetmap.org/copyright) is open data, licensed under the Open Data Commons Open Database License (ODbL) by the OpenStreetMap Foundation (OSMF).

### Dataset Descriptions

1. OpenCelliD Data

    [OpenCelliD](https://opencellid.org/) is a collaborative community project that collects GPS positions of cell towers and their corresponding location area identity. The dataset includes the locations and types of cell towers which is used to calculate proximity of a tower to a school location.

    Each cell tower location contains the following adjoining attributes:

    | Parameter | Description |
    |------------|-------------|
    | radio| Network type. One of the strings GSM, UMTS, LTE or CDMA.|
    |mcc| Mobile Country Code (UK: 234, 235)|
    |net| Mobile Network Code (MNC)|
    |area|Location Area Code (LAC) for GSM and UMTS networks. Tracking Area Code (TAC) for LTE networks. Network Idenfitication number (NID) for CDMA networks |
    |cell|Cell ID|
    |unit| Primary Scrambling Code (PSC) for UMTS networks. Physical Cell ID (PCI) for LTE networks. An empty value for GSM and CDMA networks|
    |lon|Longitude in degrees between -180.0 and 180.0 </br> If changeable=1: average of longitude values of all related measurements. </br> If changeable=0: exact GPS position of the cell tower|
    |lat| Latitude in degrees between -90.0 and 90.0 </br> If changeable=1: average of latitude values of all related measurements. </br> If changeable=0: exact GPS position of the tower|
    |range| Estimate of cell range, in meters.
    |samples|Total number of measurements assigned to the cell tower
    |changeable| Defines if coordinates of the cell tower are exact or approximate.|
    |created| The first time when the cell tower was seen and added to the OpenCellID database.|
    |updated|The last time when the cell tower was seen and updated.|
    |averageSignal| Average signal strength from all assigned measurements for the cell.|

2. Population Data

    Population data is high-resolution geospatial data on population distributions. There are several types of gridded population count datasets in the [WorldPop](https://www.worldpop.org/) Open Population Repository (WOPR). In our data gathering pipeline we used [Population Counts / Unconstrained individual countries 2000-2020 UN adjusted (1km resolution)](https://www.worldpop.org/geodata/listing?id=75) datasets from WOPR. The dataset for individual countries is available in Geotiff and ASCII XYZ format at a resolution of 30 arc (approximately 1km at the equator). We used the Geotiff image format as input and process the image to get population counts and locations for each pixel in the image.

    Each pixel contains the following adjoining attributes:

    | Field Name   | Type        | Description                                                                                        |
    |--------------|-------------|----------------------------------------------------------------------------------------------------|
    | `population` | Float       | UN adjusted population count for the pixel location.                                               |
    | `geometry`   | Geometry    | The geometry representing the pixel point location.                                                |

3. Satellite Data

    To see the full code for gathering this data, click here. To gather the satellite data, we used Google Earth Engine API for Python. We gathered three different types of data: Global Human Modification Index, Nighttime Data, and Normalized Difference Vegetation Index. Our hope with gathering this data is that it would provide an accurate proxy for households and schools with internet connection. If we knew a school was located in a place with a high average radiance, it might also mean there was high internet connectivity. The beauty of satellite data is that its continous for the entire globe. We initially struggled with learning how to crop the data for all the school points we wanted. Eventually, we set a buffer, 5 kilometers in our case, zone around each school point in both Brazil and Thailand and obtained specific satellite information that was input as a number into the training dataset. Below please find more information on each of the datasets we used including descriptions taken from the Google Earth Engine Data Catalog.

    1. Global Human Modification Index (String for Image Collection ID is: 'CSP/HM/GlobalHumanModification'):
        - The global Human Modification dataset (gHM) provides a cumulative measure of human modification of terrestrial lands globally at 1 square-kilometer resolution. The gHM values range from 0.0-1.0 and are calculated by estimating the proportion of a given location (pixel) that is modified, the estimated intensity of modification associated with a given type of human modification or "stressor". 5 major anthropogenic stressors circa 2016 were mapped using 13 individual datasets:
          - human settlement (population density, built-up areas)
          - agriculture (cropland, livestock)
          - transportation (major, minor, and two-track roads; railroads)
          - mining and energy production
          - electrical infrastructure (power lines, nighttime lights)
    2. NOAA Monthly Nighttime images using the VIIRS Satellite (String for Image Collection ID is: "NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
        - Monthly average radiance composite images using nighttime data from the Visible Infrared Imaging Radiometer Suite (VIIRS) Day/Night Band (DNB).
        - As these data are composited monthly, there are many areas of the globe where it is impossible to get good quality data coverage for that month. This can be due to cloud cover, especially in the tropical regions, or due to solar illumination, as happens toward the poles in their respective summer months. Therefore it is recommended that users of these data utilize the 'cf_cvg' band and not assume a value of zero in the average radiance image means that no lights were observed.
    3. Normalized Difference Vegetation Index Band from the MODIS dataset (String for Image Collection ID is: 'MODIS/006/MOD13A2'):
        - Normalized Difference Vegetation Index or NDVI measures the vegetation or greenness present on the Earth's surface
        - The algorithm for this product chooses the best available pixel value from all the acquisitions from the 16-day period. The criteria used are low clouds, low view angle, and the highest NDVI/EVI value.
  
    Each school location contains the following adjoining attributes:

    | Field Name                 | Type        | Description                                                                                                         |
    |----------------------------|-------------|---------------------------------------------------------------------------------------------------------------------|
    | `mean_ghm`                 | Float       | The average global human modification index for the location and year 2016                                          |
    | `mean_avg_rad`             | Float       | The average radiance for the location and given start year and end year                                             |
    | `change_year_avg_rad`      | Float       | The average yearly change of radiencebetween start year and end year for the location                               |
    | `slope_year_avg_rad`       | Float       | The average yearly slope of change of radiance between start year and end year for the location                     |
    | `change_month_avg_rad`     | Float       | The average monthly change of radiance between start year and end year for the location                             |
    | `slope_month_avg_rad`      | Float       | The average monthly slope of change of radiance between start year and end year for the location                    |
    | `mean_cf_cvg`              | Float       | The average cloud free coverage for the location and given start year and end year                                  |
    | `change_year_cf_cvg`       | Float       | The average yearly change of cloud free coverage between start year and end year for the location                   |
    | `slope_year_cf_cvg`        | Float       | The average yearly slope of change of cloud free coverage between start year and end year for the location          |
    | `change_month_cf_cvg`      | Float       | The average monthly change of cloud free coverage between start year and end year for the location                  |
    | `slope_month_cf_cvg`       | Float       | The average monthly slope of change of cloud free coverage between start year and end year for the location         |
    | `mean_NDVI`                | Float       | The average NDVI for the location and given start year and end year                                                 |
    | `change_year_NDVI`         | Float       | The average yearly change of NDVI between start year and end year for the location                                  |
    | `slope_year_NDVI`          | Float       | The average yearly slope of change of NDVI between start year and end year for the location                         |
    | `change_month_NDVI`        | Float       | The average monthly change of NDVI between start year and end year for the location                                 |
    | `slope_month_NDVI`         | Float       | The average monthly slope of change of NDVI between start year and end year for the location                        |

4. Facebook Data

    Facebook data refers to the data that we get from the [Facebook Marketing API](https://developers.facebook.com/docs/marketing-apis). The Marketing API is an HTTP-based API that you can use to programmatically query data, create and manage ads, and perform a wide variety of other tasks. Furthermore, our Facebook data mainly uses the Ads Management API under the Marketing API which has the method that provides a delivery estimate for a given ad set configuration. The Ad set refers to the collection of advertisements. For each ad set, it is possible to define delivery estimate using the [Ad Set Delivery Estimate](https://developers.facebook.com/docs/marketing-api/reference/ad-campaign/delivery_estimate/) method of the API. Two parameters are required for the delivery estimate method in order to get delivery estimate for a given location: optimization goal and dictionary that defines targeting specifications. [Optimization goal](https://developers.facebook.com/docs/marketing-api/bidding/overview#opt) can take several values such as 'clicks', 'impressions', 'replies', 'reach' etc. In our case, we used 'reach' as an optimization goal parameter since it carries out the 'reach' objective to show ads to the maximum number of people in the area. On the other hand, the [targeting specification](https://developers.facebook.com/docs/marketing-api/audiences/reference/advanced-targeting/) parameter is nicely customizable with fields such as 'geo-locations', 'interests', 'genders', 'age', 'relationship_status' and so on. In our case, we use custom locations (schools) with radius (5 kilometers) as our targeting specification and collect reach estimates for those locations.

    Each custom location contains the following adjoining attributes:

    | Field Name          | Type        | Description                                                                                                                                   |
    |---------------------|-------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
    | `estimate_dau`      | Integer     | The estimated number of people that have been active on your selected platforms and satisfy your targeting spec in the past day.              |
    | `estimate_mau`      | Integer     | The estimated number of people that have been active on your selected platforms and satisfy your targeting spec in the past month.            |
    | `estimate_ready`    | Boolean     | Whether or not an estimate is ready for the audience. Some audiences require time to populate before we can provide a delivery estimate.      |

5. Speedtest Data

    Speedtest data provides global fixed broadband and mobile (cellular) network performance metrics. The dataset provided by [Ookla Open Data Projects](https://www.ookla.com/ookla-for-good) is in zoom level 16 web mercator tiles (approximately 610.8 meters by 610.8 meters at the equator). Data is provided in both Shapefile format as well as Apache Parquet with geometries represented in Well Known Text (WKT) projected in EPSG:4326. Download speed, upload speed, and latency are collected via the Speedtest by Ookla applications and averaged for each tile.

    Each tile contains the following adjoining attributes:

    | Field Name   | Type        | Description                                                                                        |
    |--------------|-------------|----------------------------------------------------------------------------------------------------|
    | `avg_d_kbps` | Integer     | The average download speed of all tests performed in the tile, represented in kilobits per second. |
    | `avg_u_kbps` | Integer     | The average upload speed of all tests performed in the tile, represented in kilobits per second.   |
    | `avg_lat_ms` | Integer     | The average latency of all tests performed in the tile, represented in milliseconds                |
    | `tests`      | Integer     | The number of tests taken in the tile.                                                             |
    | `devices`    | Integer     | The number of unique devices contributing tests in the tile.                                       |
    | `quadkey`    | Text        | The quadkey representing the tile.                                                                 |
    | `geometry`   | Geometry    | The geometry representing the tile location and shape.                                             |

## Data Gathering and Feature Engineering Class Diagram

Our data pipeline includes three superclasses: Country, Opendata and  Feature Engineering. Country is a parent class to our school and survey classes. Opendata class is a parent class to speedtest, opencell, facebook, population and satellite open-source data classes. Finally, we coded feature engineering class in which school, survey and opendata classes are processed and merged.

### Map Offline Package Hierarchy

<div class='mermaid'>
  classDiagram
      map_offline <|-- OpenData
      map_offline <|-- FeatureEngineering
      map_offline <|-- Country
      Country <|-- School
      Country <|-- Survey
      Survey <|-- BRA_Survey
      Survey <|-- THA_Survey
      Survey <|-- PHL_Survey
      OpenData <|-- PopulationData
      OpenData <|-- SpeedtestData
      OpenData <|-- FacebookData
      OpenData <|-- OpencellData
      OpenData <|-- SatelliteData
      class map_offline{
        +training_set_vxxx
      }
      class FeatureEngineering{
        + configs
        + school_data
        + set_training_data()
        + save_training_set()
        + get_opendata()
      }
      class Country{
        + country_code
        + country_name
        + geodata
        + set_country_geometry()
      }
      class School{
        + buffer
        + data
        + set_school_data()
      }
      class Survey{
        + available_countries
        + data
      }
      class BRA_Survey{
        + set_survey_data()
      }
      class THA_Survey{
        + set_survey_data()
      }
      class PHL_Survey{
        + set_survey_data()
      }
      class OpenData{
        + country_code
        + data
      }
      class PopulationData{
        + year
        + set_pop_data()
      }
      class SpeedtestData{
        + type
        + year
        + quarter
        + set_speedtest_data()
      }
      class FacebookData{
        + locations
        + access_token
        + ad_account_id
        + call_limit
        + radius
        + set_fb_data()
      }
      class OpencellData{
        + access_token
        + set_cell_data()
      }
      class SatelliteData{
        + locations
        + start_year
        + end_year
        + buffer
        + max_call_size
        + json_key_path
        + ee_service_account
        + set_satellite_data()
      }
</div>

### Data Gathering Pipeline

We are still working on the data gathering pipeline workflow...

1. Country

    Country class takes input argument of country code in ISO 3166-1 alpha-3 format and initialize the following attributes:

    | Attribute Name        | Description                  | Type            |
    | --------------------- | ---------------------------- | --------------- |
    | `country_code`        | Country code                 | Text            |
    | `geodata`             | country boundaries geometry  | Geometry        |
    | `country_name`        | Country name                 | Text            |

    1. School
  
        School class inherits the Country class. It has additional attributes of **working directory**, **buffer** and **data** over the Country class. Working directory attribute refers to the folder where school datasets are kept and the buffer can be any nonnegative number to define a radius in kilometers around a school location. Data attribute is assigned by set_school_data method which has the following logic:
  
        ```{}
        IF school_latlon_{country_code} exists in the directory THEN
          READ school latitude-longitude pairs
        else
          CALL get_osm_schools() FROM opendata_scrap
              GET school lat-lon pairs from OpenStreetMap
          WRITE school_latlon_{country_code}.csv to directory
        DROP duplicated schools that have same lat-lon pair
        INIT school_location column with point geometry of school
        CALCULATE approximate radians distance FROM kilometers
        ADD buffer to the point location
        INIT geometry columns with school buffer zone polygon geometry
        SET data attribute with source_school_id, latitude, longitude, school_location, geometry columns
        ```

        School class sets the data attribute when the class is initialized and the data attribute keeps school dataset with following variables:

        | Field Name         | Type        | Description                                               |
        |--------------------|-------------|-----------------------------------------------------------|
        | `source_school_id` | Text        | Identifier for the school.                                |
        | `latitude`         | Float       | Latitude of the school.                                   |
        | `longitude`        | Float       | Longitude of the school.                                  |
        | `school_location`  | Geometry    | Point location of the school.                             |
        | `geometry`         | Geometry    | Polygon of school buffer zone.                            |

    2. Survey

        Survey class inherits the Country class. In addition to Country class attributes, Survey class keeps **available countries** and **data** as attribute. We observed that for each country survey dataset spatial resolution and target variable are in the various format. Therefore, we added different subclasses for each country that we worked on. Those subclasses read the raw survey data from the survey/{country_name} folder. If the survey dataset does not already include geometry object, then country geo-data having spatial resolution higher than or equal to raw survey data, e.g. barrangays, provinces, enumeration areas, can be used to get geometries for individuals or households survey data. After, each survey instance matched with geo-data, target variable needs to be aggregated on the area level in order to get the proportion of the connected participants. As a result, data attribute assigned by the country survey class which are called inside the Survey superclass with the following logic:
  
        ```{}
        IF country_code IN available_countries THEN
            CALL country survey class, {COUNTRY_CODE}_Survey
            SET data attribute with target and geometry columns
            WRITE survey_{country_code}.csv to directory
        ELSE
            SET data attribute to None, continue without ground truth
        ```
  
        Country survey class sets the data attribute if country code exists in the available countries attribute. The data attribute keeps survey dataset with following variables:

        | Field Name         | Type        | Description                                               |
        |--------------------|-------------|-----------------------------------------------------------|
        | `target`           | Float       | Target value for the area/region.                         |
        | `geometry`         | Geometry    | Polygon geometry of the area/region                       |

2. OpenData

    OpenData class takes input argument of country code in ISO 3166-1 alpha-3 format and initialize the following attributes:

    | Attribute Name        | Description                  | Type            |
    | --------------------- | ---------------------------- | --------------- |
    | `country_code`        | Country code                 | Text            |
    | `country_geo`         | Country boundaries geometry  | Geometry        |
    | `country_name`        | Country name                | Text            |
    | `data`                | Data                         | DataFrame       |
    | `base_wd`             | Path to data folder          | Text            |

    1. PopulationData

        PopulationData class inherits the OpenData class. Population dataset **year** and **working directory** are input arguments for this class. Working directory attribute, **wd**, points out the 'worldpop' folder. PopulationData has the `set_pop_data` method with the following logic:

        ```{}
        IF school_agg_pop_{country_code}, school joined population data, exists in the directory THEN
            SET data attribute to None
        ELSE
            CALL get_pop_url() FROM opendata_scrap
            INIT pop_name with population dataset name and pop_url with population dataset url
            IF pop_name exists in the directory THEN
                READ pop_name geotiff file
            ELSE
                GET pop_name geotiff file from pop_url
            CALL tif_to_gdf() FROM opendata_utils
                INIT geodataframe with population and point geometry of geotiff pixels
            SET data attribute with population and geometry columns
        ```

    2. SpeedtestData

        SpeedtestData class is another subclass of the OpenData class. SpeedtestData class takes **type**, **year** and **quarter** input arguments to initialize the SpeedtestData object. The **wd** attribute points out the 'speedtest' folder. Data attribute is set by set_speedtest_data method and called during the class initialization. Method `set_speedtest_data` has the following structure:

        ```{}
        CALL get_speedtest_url() FROM opendata_scrap
        INIT tile_url with speedtest dataset url and tile_name with speedtest dataset name
        INIT country_tile_path with tile_name and country_code
        IF country_tile_path in the directory THEN
            READ country speedtest data
            CALL df_to_gdf() FROM opendata_utils
            SET data attribute with country speedtest geodataframe
        ELSE
            IF raw speedtest data is in the directory THEN
                READ speedtest data
                CALL tile_prep() inside class method
            ELSE
                GET raw speedtest dataset from tile_url
                CALL tile_prep() inside class method
        ```

        Furthermore, `tile_prep` method does the following:

        ```{}
        JOIN the speedtest tiles with country_geo attribute
        SET data attribute with 'avg_d_kbps', 'avg_u_kbps' and 'geometry' columns
        WRITE country speedtest data to directory
        ```

    3. FacebookData

        FacebookData class require **locations**, Facebook Marketing API *access_token*, Facebook Developers Sandbox **ad acccount id**, hourly **call limit** for Facebook ad services methods and **radius** attributes while initalizing the class. Working directory attribute, **wd**, is set as 'facebook' and **data** is set by `set_fb_data` method that does the following:

        ```{}
        INIT file_name as facebook_{country_code}_{facebook school data length}
        IF file_name is in the directory THEN
            READ country school facebook data from the directory
            SET data attribute with source_school_id, estimate_dau, estimate_mau and estimate_ready columns
        ELSE
            CALL get_delivery_estimate() method FROM opendata_facebook
            SET data attribute with source_school_id, estimate_dau, estimate_mau and estimate_ready columns
            WRITE country school facebook data as facebook_{country_code}_{facebook school data length}.csv to the directory
        ```

        Method `get_delivery_estimate` from `opendata_facebook.py` described below:

        ```{}
        CALL fb_api_init() method with access token and ad account id
        INIT api and my_account as Facebook Marketing API object
        INIT estimate_dict empty dictionary to keep the data
        SPLIT locations into chunks that have length less than maximum hourly call size
        FOR each chunk in chunks
            FOR each school in chunk
                TRY
                    CALL point_delivery_estimate() method with my_account, school latitude, school longitude and radius
                    APPEND the output of the point_delivery_estimate() to estimate_dict
                EXCEPT
                    APPEND 0, 0 and False as delivery estimate output which indicates number of users around the school is below the threshold
            END FOR
            STOP for 1 hour
        END FOR
        RETURN dataframe of estimate_dict
        ```

    4. OpencellData

        OpencellData is a child class of the parent OpenData class. It's working directory, **wd**, attribute points out to 'opencellid' folder. If the country OpenCelliD data does not exist in the directory it requires access token to OpenCelliD Project database. In class method of `set_cell_data` has the following structure:

        ```{}
        IF country opencell data, {country_code}.csv.gz, in the directory THEN
            READ country opencell data
            CALL df_to_gdf() FROM opendata_utils
            SET data attribute with country opencell data
        ELSE
            CALL get_cell_data() from opendata_scrap
            GET raw country opencell data by get_cell_data()
            CALL tile_prep() inside class method
            SET data attrribute with 'radio', 'range' and 'geometry' columns
            WRITE compressed country opencell data to directory as {country_code}.csv.gz
        ```

    5. SatelliteData

        SatelliteData object, subclass of OpenData, require **locations**, **start year**, **end year**, **buffer**, Google Earth Engine API maximum feature collection **call length**, Google services **key file in 'json' format**, **Google services account email address** and **the scale** of the image at which to request inputs to a computation is determined from the output, attributes at the initialization phase. Moreover, **wd** is set as 'satellite' by default and **data** attribute is set by `set_satellite_data` method with the following pseudocode:

        ```{}
        SET collection_band with image collections and bands specified in configs.py
        IF satellite_{country_code}, country satellite data, is in the directory THEN
            READ country satellite data from the directory
            SET data attribute with source_school_id and collection_band values
        ELSE
            CALL get_satellite_data() method FROM opendata_satellite
            SET data attribute with source_school_id and collection_band values
            WRITE country satellite data as satellite_{country_code}.csv to the directory
        ```

        Method `get_satellite_data` from `opendata_satellite.py` described below:

        ```{}
        CALL gee_init() method with key.json and google services account
        INIT Google Earth Engine API
        INIT df_sat empty dataframe to keep data
        SPLIT locations into chunks that have length less than maximum call size
        FOR each chunk in chunks
            CALL get_feature_collection() method with locations in the chunk and buffer
            INIT feature_collection with the output of get_feature_collection()
            FOR each collection and bands in collection_band
                IF bands is empty for image collection THEN
                    CALL Image_Processing() method with collection, feature_collection and scale
                    INIT mean_{collection_name} with the output of Image_Processing()
                ELSE
                    FOR each band in bands
                        CALL Slope_Image_Processing() method with collection, feature_collection, band, start_year, end_year and scale
                        INIT mean_{band}, change_year_{band} and slope_year_{band} with the output of Slope_Image_Processing()
                        CALL Monthly_Slope_Image_Processing() method with collection, feature_collection, band, start_year, end_year and scale
                        INIT change_month_{band} and slope_month_{band} with the output of Slope_Image_Processing()
                    END FOR
            END FOR
            CONCATENATE initialized variables for the chunk to df_sat
        END FOR
        RETURN df_sat
        ```

3. FeatureEngineering

## Training Data Dictionary

Show a table of each of the predictor in the training set and what their definitions are:

| Variable Name              | Description                                                                                           | Data Source                                      |
| -------------------------- | ----------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| `avg_d_kbps`               | Average Download Speed                                                                                | Speedtest Data                                   |
| `avg_u_kbps`               | Average Upload Speed                                                                                  | Speedtest Data                                   |
| `estimate_dau`             | Facebook Daily Active Users estimate                                                                  | Facebook Data                                    |
| `estimate_mau`             | Facebook Monthly Active Users estimate                                                                | Facebook Data                                    |
| `population`               | Population around school buffer zone                                                                  | Population Data                                  |
| `mean_ghm`                 | Mean Global Human Modification value                                                                  | Satellite Data - Global Human Modification Index |
| `mean_avg_rad`             | Mean value from the Average Radiance band                                                             | Satellite Data - VIIRS Nighttime DNB             |
| `mean_cf_cvg`              | Mean value from the cloud free coverage band                                                          | Satellite Data - VIIRS Nighttime DNB             |
| `slope_year_avg_rad`       | The yearly rate of change between 2019 and 2014 of Average Radiance                                   | Satellite Data - VIIRS Nighttime DNB             |
| `change_year_avg_rad`      | The change between the average values of 2019 and 2014 of Average Radiance                            | Satellite Data - VIIRS Nighttime DNB             |
| `slope_year_cf_cvg`        | The yearly rate of change between 2019 and 2014 from the Cloud Free Coverage Band                     | Satellite Data - VIIRS Nighttime DNB             |
| `change_year_cf_cvg`       | The change between the average values of 2019 and 2014 from the Cloud Free Coverage Band              | Satellite Data - VIIRS Nighttime DNB             |
| `slope_month_avg_rad`      | The monthly rate of change between 2019 and 2014 of the Average Radiance Band                         | Satellite Data - VIIRS Nighttime DNB             |
| `change_month_avg_rad`     | The change between the average of Dec 2019 and Jan 2014 of the Average Radiance Band                  | Satellite Data - VIIRS Nighttime DNB             |
| `slope_month_cf_cvg`       | The monthly rate of change between 2019 and 2014 from the Cloud Free Coverage Band                    | Satellite Data - VIIRS Nighttime DNB             |
| `change_month_cf_cvg`      | The rate of change between the average of Dec 2019 and Jan 2014 from the Cloud Free Coverage Band     | Satellite Data - VIIRS Nighttime DNB             |
| `mean_NDVI`                | The average value of the Vegetation Index                                                             | Satellite Data - MODIS Dataset                   |
| `slope_year_NDVI`          | The yearly rate of change between 2019 and 2014 of the Vegetation Index                               | Satellite Data - MODIS Dataset                   |
| `change_year_NDVI`         | The change between 2019 and 2014 of the Vegetation Index                                              | Satellite Data - MODIS Dataset                   |
| `slope_month_NDVI`         | The monthly rate of change between 2019 and 2014 of the Vegetation Index                              | Satellite Data - MODIS Dataset                   |
| `change_month_NDVI`        | The change between the average of May 2019 and May 2014 of the Vegetation Index                       | Satellite Data - MODIS Dataset                   |
| `range`                    | The binary variable that checks whether there is opencell tower in the to the school area             | OpenCelliD Data                                  |

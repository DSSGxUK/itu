

from osgeo import gdal
#from pyproj import Transformer
import geopandas as gp
import os

from data_gathering.opendata_utils import *
from data_gathering.opendata_scrap import *
from school import *
from data_gathering.opendata_facebook import *
from feature_engineering import configs
from data_gathering.opendata_satellite import *


"""OPENDATA SUPERCLASS"""
class OpenData:

    def __init__(self, country_code, data=None, base_wd = '../../../data/'):
        self.data = data
        self.base_wd = base_wd  ### Please edit the base wd to your data folder!
        self.country_code = country_code
        self.set_country_geo()

    def set_country_geo(self):
        country = Country(self.country_code)
        self.country_geo = country.geodata
        self.country_name = country.country_name


""""POPULATION DATA CLASS"""
class PopulationData(OpenData):

    def __init__(self, country_code, wd = 'worldpop/', year= configs.POPULATION_DATASET_YEAR):
        super().__init__(country_code)
        self.wd = self.base_wd + wd
        self.year = year
        self.set_pop_data()

    def set_pop_data(self):

        file_name = 'school_agg_pop_'+self.country_code.lower()+'.csv'

        if os.path.exists(self.wd + file_name):
            print('No need to read raw population data; school joined data is exist in directory!')
            self.data = None
            
        else:
            pop_url, pop_name = get_pop_url(self.country_code, self.year)
            # CHECK tif FILE IS ALREADY IN THE DIRECTORY
            if os.path.exists(self.wd + pop_name):
                print('Reading population tif file...')
                try:
                    pop = gdal.Open(self.wd + pop_name)
                except:
                    raise RuntimeError('Unable to open ' + pop_name)

            else:
                print('Downloading population data...')
                try:
                    pop = gdal.Open(pop_url)
                except:
                    raise RuntimeError('Unable to download from ' + pop_url)

            self.data = tif_to_gdf(pop)



"""SPEEDTEST DATA CLASS"""
class SpeedtestData(OpenData):

    def __init__(self, country_code, wd='speedtest/', type=configs.SPEEDTEST_TILE_TYPE, year=configs.SPEEDTEST_TILE_YEAR, quarter=configs.SPEEDTEST_TILE_QUARTER):
        super().__init__(country_code)
        self.wd = self.base_wd + wd
        self.type = type
        self.year = year
        self.quarter = quarter
        self.tile_url, self.tile_name = get_speedtest_url(self.type, self.year, self.quarter)
        self.set_speedtest_data()

    def set_speedtest_data(self):
        country_tile_path = self.wd + self.tile_name[:-4] + '_' + self.country_code.lower() + '.csv'

        # CHECK IF COUNTRY SPEEDTEST DATA IS ALREADY IN THE DIRECTORY
        if os.path.exists(country_tile_path):
            print('Reading speedtest data for ' + self.country_name + '...')
            df_tiles = pd.read_csv(country_tile_path)
            gdf_tiles = df_to_gdf(df_tiles)
            self.data = gdf_tiles[['avg_d_kbps', 'avg_u_kbps', 'geometry']]
        else:
            # CHECK SPEEDTEST DATA IS ALREADY IN THE DIRECTORY
            if os.path.exists(self.wd + str(self.tile_name)):
                print('Reading speedtest data...')
                try:
                    gdf_tiles = gp.read_file(self.wd + str(self.tile_name))
                    self.data = gdf_tiles
                    print('Getting tiles for ' + self.country_name + '...')
                    self.data = self.tile_prep()
                except:
                    raise RuntimeError('Unable to read ' + self.tile_name)

            else:
                print('Downloading speedtest data...')
                try:
                    gdf_tiles = gp.read_file(self.tile_url)
                    self.data = gdf_tiles
                    print('Getting tiles for ' + self.country_name + '...')
                    self.data = self.tile_prep()
                except:
                    raise RuntimeError('Unable to download from ' + self.tile_url)

    
    def tile_prep(self):
        tiles = gp.sjoin(self.data, self.country_geo, how="inner", op="within")
        tiles = tiles[['avg_d_kbps', 'avg_u_kbps', 'geometry']]

        country_tile_path = self.wd + self.tile_name[:-4] + '_' + self.country_code.lower() + '.csv'

        print('Writing country speedtest data to directory...')
        tiles.to_csv(country_tile_path, index=False)
        return tiles


"""FACEBOOK DATA CLASS"""
class FacebookData(OpenData):

    def __init__(self, country_code, wd = 'fb/', locations = None, access_token=configs.FACEBOOK_MARKETING_API_ACCESS_TOKEN, ad_account_id=configs.FACEBOOK_AD_ACCOUNT_ID, call_limit=configs.FACEBOOK_CALL_LIMIT, radius=configs.FACEBOOK_RADIUS):
        super().__init__(country_code)
        self.wd = self.base_wd + wd
        self.locations = locations
        self.access_token = access_token
        self.ad_account_id = ad_account_id
        self.call_limit = call_limit
        self.radius = radius
        self.set_fb_data()
    
    def set_fb_data(self):

        file_name = 'facebook_' + self.country_code.lower() + '_' + str(configs.FACEBOOK_SCHOOL_DATA_LEN[self.country_code.lower()]) + '.csv'

        if os.path.exists(self.wd + file_name):
            print('Reading FB data...')
            try:
                self.data = pd.read_csv(self.wd + file_name)
            except:
                raise RuntimeError('Unable to read facebook data!')

        else:
            if self.locations is None:
                raise ValueError('Locations data frame should be provided!')
            if not set(['source_school_id', 'latitude', 'longitude']).issubset(self.locations.columns):
                raise ValueError('Locations data frame should include source_school_id, latitude and longitude columns!')

            try:
                self.data = get_delivery_estimate(self.locations, self.access_token, self.ad_account_id, self.call_limit, self.radius)
                print('Writing facebook data to directory...')
                self.data.to_csv(self.wd + 'facebook_' + self.country_code.lower() + '_' + str(len(self.locations)) + '.csv', index=False)
            except:
                raise RuntimeError('Unable to call the FB API!')


"""OPENCELL DATA CLASS"""
class OpencellData(OpenData):

    def __init__(self, country_code, wd = 'opencellid/', access_token=configs.OPENCELLID_ACCESS_TOKEN):
        super().__init__(country_code)
        self.wd = self.base_wd + wd
        self.access_token = access_token
        self.set_cell_data()

    def set_cell_data(self):

        if os.path.exists(self.wd + self.country_code + '.csv.gz'):
            print('Reading cell data...')
            try:
                self.data = pd.read_csv(self.wd + self.country_code + '.csv.gz')
                self.data = df_to_gdf(self.data)
            except:
                raise RuntimeError('Unable to read cell data!')

        else:
            try:
                print('Downloading cell data...')
                self.data = get_cell_data(self.country_code, self.access_token, self.wd)
                print('Preprocessing cell data...')
                self.data = self.cell_prep()
            except:
                raise RuntimeError('Unable to download opencell data!')

    
    def cell_prep(self):

        # Categorize radio
        self.data['radio'] = self.data.radio.astype('category')

        # Created and updated to datetime integers
        self.data['created'] = pd.to_datetime(self.data['created'], unit='s', origin='unix')
        self.data['updated'] = pd.to_datetime(self.data['updated'], unit='s', origin='unix')

        # Filter out outliers created before 2003
        self.data = self.data[self.data.created.dt.year >= 2003]

        self.data['geometry'] = [Point(i, j) for i,j in zip(self.data.lon, self.data.lat)]

        self.data = self.data[['radio', 'range', 'geometry']]

        print('Writing country opencellid data to directory...')
        self.data.to_csv(self.wd + self.country_code + '.csv.gz', compression='gzip', index=False)

        return gp.GeoDataFrame(self.data)

        

"""SATELLITE IMAGERY CLASS"""
class SatelliteData(OpenData):

    def __init__(self, country_code, wd = 'satellite/', locations = None, start_year = configs.SATELITTE_START_YEAR, end_year = configs.SATELITTE_END_YEAR, buffer = configs.SATELITTE_BUFFER, max_call_size = configs.SATELITTE_MAX_CALL_SIZE, json_key_path = configs.GOOGLE_EARTH_ENGINE_API_JSON_KEY, ee_service_account = configs.GOOGLE_SERVICES_ACCOUNT):
        super().__init__(country_code)
        self.wd = self.base_wd + wd
        self.collection_band = configs.SATELITTE_COLLECTIONS
        self.locations = locations
        self.buffer = buffer * 1000
        self.max_call_size = max_call_size

        if json_key_path is not None:
            self.json_key_path = self.wd + json_key_path

        self.ee_service_account = ee_service_account

        if start_year >=2014:
            self.start_year = start_year
        else:
            raise ValueError('Start year must be at least 2014!')

        self.end_year = end_year
        self.set_satellite_data()

    
    def set_satellite_data(self):

        if os.path.exists(self.wd + 'satellite_' + self.country_code.lower() + '.csv'):
            print('Reading satellite data from directory...')
            self.data = pd.read_csv(self.wd + 'satellite_' + self.country_code + '.csv')
        else:
            if self.locations is None:
                raise ValueError('Locations data frame should be provided!')
            if not set(['source_school_id', 'latitude', 'longitude', 'school_location']).issubset(self.locations.columns):
                raise ValueError('Locations data frame should include source_school_id, latitude, longitude and school_location columns!')
            
            print('Calling Google Earth Engine API for satellite imagery..')
            self.data = get_satellite_data(self.collection_band, self.locations, self.json_key_path, self.ee_service_account, self.buffer, self.max_call_size, self.start_year, self.end_year)
            
            print('Writing satellite data to directory...')
            self.data.to_csv(self.wd + 'satellite_' + self.country_code.lower() + '.csv', index=False)
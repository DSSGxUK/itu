import base64
import json
import numpy as np
from math import ceil
import geopandas as gp
import pandas as pd
import ee
import geemap
import os

def gee_init(key_json, service_account):

    print('Initializing the Google Earth Engine API...')
    with open(key_json) as jsonfile:
        data = json.load(jsonfile)
        datastr = json.dumps(data)
        encoded = base64.b64encode(datastr.encode())

    # only use the key when I'm in my test env
    if 'EE_PRIVATE_KEY' in os.environ:
        # key need to be decoded in a file to work 
        content = base64.b64decode(os.environ['EE_PRIVATE_KEY']).decode()
        with open(key_json, 'w') as f:
            f.write(content)
        
        # connection to the service account
        try:
            credentials = ee.ServiceAccountCredentials(service_account, key_json)
            ee.Initialize(credentials)
        except:
            raise RuntimeError('Unable to initialize Googe Earth Engine API!')

    else:
        try:
            ee.Initialize()
        except:
            raise RuntimeError('Unable to initialize Googe Earth Engine API!')


"""RETURNS VALUE LIST FROM IMAGE COLLECTION WITHOUT BAND SPECIFICATION, i.e. GLOBAL HUMAN MODIFICATION"""
def Image_Processing(image_collection, feature_collection):
    # Taking the mean of the image collection
    image_col = ee.ImageCollection(image_collection).mean()

    # Reducing the mean of the entire image collection into one number for each school buffer zone
    Processed_Img = image_col.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=30)

    # .GetInfo() actually gets the number for each buffer zone
    Dict = Processed_Img.getInfo()

    # Adds the dictionary of numbers into a value list
    val_list = [Dict['features'][i]['properties']['mean'] for i in range(len(Dict['features']))]

    return val_list


"""RETURNS AVERAGE, YEARLY CHANGE, YEARLY SLOPE OF CHANGE OF BAND VALUES BETWEEN INPUTTED YEARS"""
def Slope_Image_Processing(image_collection, feature_collection, band, start_year, end_year):

    # Mean for imagery
    print('Collecting image for ' + str(end_year - start_year + 1) + ' years...')
    mean_image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(str(start_year)+'-01-01', str(end_year)+'-12-31')).select(band).mean()
    
    print('Collecting image for year ' + str(start_year) + '...')
    start_image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(str(start_year)+'-01-01', str(start_year)+'-12-31')).mean()

    print('Collecting image for year ' + str(end_year) + '...')
    end_image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(str(end_year)+'-01-01', str(end_year)+'-12-31')).mean()

    print('Getting processed image for ' + str(end_year - start_year + 1) + ' years...')
    Processed_Img = mean_image.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=30)

    print('Calculating and getting processed image for change between years...')
    calculate_change = (end_image.select(band).subtract(start_image.select(band)))
    Processed_Img_Change = calculate_change.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=30)
    
    print('Calculating and getting processed image for slope between years...')
    calculate_slope = (end_image.select(band).subtract(start_image.select(band))).divide(end_year-start_year+1)
    Processed_Img_Slope = calculate_slope.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=30)

    Dict = Processed_Img.getInfo()
    Dict1 = Processed_Img_Change.getInfo()
    Dict2 = Processed_Img_Slope.getInfo()
    
    mean_list = [Dict['features'][i]['properties']['mean'] for i in range(len(Dict['features']))]
    change_year_list = [Dict1['features'][i]['properties']['mean'] for i in range(len(Dict1['features']))]
    slope_year_list = [Dict2['features'][i]['properties']['mean'] for i in range(len(Dict2['features']))]
    
    return mean_list, change_year_list, slope_year_list


"""RETURNS MONTHLY CHANGE AND MONTHLY SLOPE OF CHANGE OF BAND VALUES BETWEEN INPUTTED YEARS"""
def Monthly_Slope_Image_Processing(image_collection, feature_collection, band, start_year, end_year):

    print('Collecting image for ' + str(end_year - start_year + 1) + ' years...')
    image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(str(start_year)+'-01-01', str(end_year)+'-12-31'))
    
    start_image = image.sort('system:time_end').first()

    end_image = image.sort('system:time_end',False).first()

    print('Calculating and getting processed image for monthly change between years...')
    calculate_change = (end_image.select(band).subtract(start_image.select(band)))
    Processed_Img_Change = calculate_change.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=30)
    
    print('Calculating and getting processed image for monthly slope between years...')
    calculate_slope = (end_image.select(band).subtract(start_image.select(band))).divide(image.size().getInfo())
    Processed_Img_Slope = calculate_slope.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=30)

    Dict1 = Processed_Img_Change.getInfo()
    Dict2 = Processed_Img_Slope.getInfo()

    change_month_list = [Dict1['features'][i]['properties']['mean'] for i in range(len(Dict1['features']))]
    slope_month_list = [Dict2['features'][i]['properties']['mean'] for i in range(len(Dict2['features']))]
    
    return change_month_list, slope_month_list

"""GET FEATURE COLLECTION FROM SCHOOL POINT LOCATION"""
def get_feature_collection(points, buffer):
    #Converting geopandas series, the point school locations to json
    roi = gp.GeoSeries(points['school_location']).to_json()
    # convert dictionary string to dictionary
    res = json.loads(roi)
    #Converts dictionary object into a feature collection
    feature_collection = geemap.geojson_to_ee(res, geodesic=True)
    #Setting a buffer
    feature_collection = feature_collection.map(lambda f: f.buffer(buffer))
    return feature_collection


def get_satellite_data(collection_band_dict, locations, json_key_path, ee_service_account, buffer, max_call_size, start_year, end_year):
    gee_init(json_key_path, ee_service_account)
    df_sat = pd.DataFrame()
    no_chunks = ceil(len(locations)/max_call_size)
    print('Satellite data will be read in total of ' + str(no_chunks) + ' chunk(s)!')
    for c_no, chunk in enumerate(np.array_split(locations, no_chunks)):
        
        print('Getting satellite data for the chunk ' + str(c_no) + '...')
        satellite_dict = {}
        satellite_dict['source_school_id'] = np.array(chunk.source_school_id)
        feature_collection = get_feature_collection(chunk, buffer)
        
        for collection, bands in zip(collection_band_dict.keys(), collection_band_dict.values()):
            print('Collecting from ' + collection + '...')
            if bands==None:
                if 'Modification' in collection:
                    print('Collecting mean_ghm...')
                    satellite_dict['mean_ghm'] = Image_Processing(collection, feature_collection)
            else:
                for band in bands:
                    print('Collecting ' + band + '...')
                    satellite_dict['mean_' + band], satellite_dict['change_year_' + band], satellite_dict['slope_year_' + band] = Slope_Image_Processing(collection, feature_collection, band, start_year, end_year)
                    satellite_dict['change_month_' + band], satellite_dict['slope_month_' + band] = Monthly_Slope_Image_Processing(collection, feature_collection, band, start_year, end_year)
        
        df_sat = pd.DataFrame(pd.concat([df_sat, pd.DataFrame(satellite_dict)], ignore_index=True))
    
    return df_sat
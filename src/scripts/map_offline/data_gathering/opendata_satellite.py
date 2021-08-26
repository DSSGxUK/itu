
"""LOAD DEPENDENCIES"""
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
def Image_Processing(image_collection, feature_collection, scale):
    # Taking the mean of the image collection
    print('Processing image and calculating means...')
    image_col = ee.ImageCollection(image_collection).mean()

    # Reducing the mean of the entire image collection into one number for each school buffer zone
    Processed_Img = image_col.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=scale)

    # .GetInfo() actually gets the number for each buffer zone
    Dict = Processed_Img.getInfo()

    # Adds the dictionary of numbers into a value list
    val_list = [Dict['features'][i]['properties']['mean'] for i in range(len(Dict['features']))]

    return val_list


"""RETURNS AVERAGE, YEARLY CHANGE, YEARLY SLOPE OF CHANGE OF BAND VALUES BETWEEN INPUTTED YEARS"""
def Slope_Image_Processing(image_collection, feature_collection, band, start_year, end_year, scale):

    if band == 'NDVI':
        slope_start_date = [str(start_year) + '-04-01', str(start_year) + '-05-01']
        slope_end_date = [str(end_year) + '-04-01', str(end_year) + '-05-01']
    else:
        slope_start_date = [str(start_year)+'-01-01', str(start_year)+'-12-31']
        slope_end_date = [str(end_year)+'-01-01', str(end_year)+'-12-31']

    # Mean for imagery
    print('Collecting image for ' + str(end_year - start_year + 1) + ' years...')
    mean_image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(str(start_year)+'-01-01', str(end_year)+'-12-31')).select(band).mean()
    
    print('Collecting image for year ' + str(start_year) + '...')
    start_image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(slope_start_date[0], slope_start_date[1])).mean()

    print('Collecting image for year ' + str(end_year) + '...')
    end_image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(slope_end_date[0], slope_end_date[1])).mean()

    print('Processing image and calculating mean of ' + str(end_year - start_year + 1) + ' years...')
    Processed_Img = mean_image.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=scale)
    Dict = Processed_Img.getInfo()
    mean_list = [Dict['features'][i]['properties']['mean'] for i in range(len(Dict['features']))]

    print('Processing image and calculating change between years...')
    calculate_change = (end_image.select(band).subtract(start_image.select(band)))
    Processed_Img_Change = calculate_change.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=scale)
    Dict1 = Processed_Img_Change.getInfo()
    change_year_list = [Dict1['features'][i]['properties']['mean'] for i in range(len(Dict1['features']))]
    
    print('Calculating slope between years...')
    slope_year_list = change_year_list/np.repeat(end_year-start_year+1, len(change_year_list))
    
    return mean_list, change_year_list, slope_year_list


"""RETURNS MONTHLY CHANGE AND MONTHLY SLOPE OF CHANGE OF BAND VALUES BETWEEN INPUTTED YEARS"""
def Monthly_Slope_Image_Processing(image_collection, feature_collection, band, start_year, end_year, scale):

    if band == 'NDVI':
        slope_date = [str(start_year) + '-04-01', str(end_year) + '-05-01']
    else:
        slope_date = [str(start_year) + '-01-01', str(end_year) + '-12-31']

    print('Collecting monthly image for ' + str(end_year - start_year + 1) + ' years...')
    image = ee.ImageCollection(image_collection).filter(
        ee.Filter.date(slope_date[0], slope_date[1]))
    
    start_image = image.sort('system:time_end').first()

    end_image = image.sort('system:time_end',False).first()

    print('Processing image and calculating monthly change between years...')
    calculate_change = (end_image.select(band).subtract(start_image.select(band)))
    Processed_Img_Change = calculate_change.reduceRegions(feature_collection, ee.Reducer.mean(), crs='epsg:4326', scale=scale)
    Dict1 = Processed_Img_Change.getInfo()
    change_month_list = [Dict1['features'][i]['properties']['mean'] for i in range(len(Dict1['features']))]
    
    print('Calculating monthly slope between years...')
    slope_month_list = change_month_list/np.repeat(image.size().getInfo(), len(change_month_list))
    
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


def get_satellite_data(collection_band_dict, locations, json_key_path, ee_service_account, buffer, max_call_size, start_year, end_year, scale):
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
                    satellite_dict['mean_ghm'] = Image_Processing(collection, feature_collection, scale)
            else:
                for band in bands:
                    print('Collecting ' + band + '...')
                    satellite_dict['mean_' + band], satellite_dict['change_year_' + band], satellite_dict['slope_year_' + band] = Slope_Image_Processing(collection, feature_collection, band, start_year, end_year, scale)
                    satellite_dict['change_month_' + band], satellite_dict['slope_month_' + band] = Monthly_Slope_Image_Processing(collection, feature_collection, band, start_year, end_year, scale)
        
        df_sat = pd.DataFrame(pd.concat([df_sat, pd.DataFrame(satellite_dict)], ignore_index=True))
    
    return df_sat
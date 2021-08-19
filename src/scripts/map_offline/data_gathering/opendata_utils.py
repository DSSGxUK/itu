
"""LOAD DEPENDENCIES"""
import sys
import numpy as np
from shapely.geometry import Point
import geopandas as gp
from shapely import wkt


"""tif_to_gdf to get data from tif file as geopandas df"""
def tif_to_gdf(tif):
    print('Getting values from tif file...')
    try:
        srcband = tif.GetRasterBand(1).ReadAsArray()
    except RuntimeError as e:
        print('Band 1 not found')
        print(e)
        sys.exit(1)
    
    flat = srcband.flatten()
    flat = np.where(flat == -99999, 0, flat)
    
    gt = tif.GetGeoTransform()
    
    res = gt[1]
    
    xmin = gt[0]
    ymax = gt[3]
    
    xsize = tif.RasterXSize
    ysize = tif.RasterYSize
    
    xstart = xmin + res/2
    ystart = ymax - res/2
    
    x = np.arange(xstart, xstart + xsize*res, res)
    y = np.arange(ystart, ystart - ysize*res, -res)
    
    x = np.tile(x, ysize)
    y = np.repeat(y, xsize)
    
    print('Creating geometries; this might take a few minutes...')
    geometry = [Point(ij) for ij in zip(x,y)]
    
    tif_dict = {'population': flat, 'geometry': geometry}
    print('Creating geo dataframe; this might take a few minutes...')
    return gp.GeoDataFrame(tif_dict, crs='EPSG:4326')


"""df_to_gdf to convert pandas df to geopandas df"""
def df_to_gdf(df):
    df['geometry'] = df['geometry'].apply(wkt.loads)
    if 'school_location' in df.columns:
        df['school_location'] = df['school_location'].apply(wkt.loads)
    return gp.GeoDataFrame(df, crs='EPSG:4326')

"""LOAD DEPENDENCIES"""
import os
import geopandas as gp
import pandas as pd
from shapely.geometry import Point
#from math import radians, cos


""" LOAD MODULES"""
from country import *
from data_gathering.opendata_scrap import osm_to_json, get_osm_schools



"""SCHOOL CLASS AS SUBCLASS OF COUNTRY"""
class School(Country):

    def __init__(self, country_code, wd = configs.WD + 'data/school_loc/', buffer=0.01):
        super().__init__(country_code)
        self.wd = wd ### Please edit the wd to your school data folder!
        self.country_code = country_code
        self.buffer = buffer
        self.set_school_data()

    

    """function to get raw school location data"""
    def set_school_data(self):
        if os.path.exists(self.wd + 'school_latlon_' + self.country_code.lower() + '.csv'):
            print('Reading school data...')
            try:
                self.data = pd.read_csv(self.wd + 'school_latlon_' + self.country_code.lower() + '.csv')
            except:
                raise RuntimeError('Error reading the school location data!')
        else:
            print('Gettin school location data from OpenStreetMap database...')
            self.data = get_osm_schools(self.country_code)
            self.data.to_csv(self.wd + 'school_latlon_' + self.country_code.lower() + '.csv', index=False)
        
        self.data = self.school_prep()


    """function to prepare raw school location data"""
    def school_prep(self):
        # drop latlon duplicates
        self.data.drop(index=self.data[self.data[['latitude', 'longitude']].duplicated()].index.tolist(), inplace=True)
        self.data['school_location'] = [Point(i, j) for i, j in zip(self.data.longitude, self.data.latitude)]

        if self.buffer != 0:
            print('Creating buffer zones for schools...')
            self.data['geometry'] = [Point(i, j).buffer(self.buffer) for i, j in zip(self.data.longitude, self.data.latitude)]

            # if you want more precise approximation for radians to km uncomment following line of code
            #self.data['geometry'] = [Point(i, j).buffer(self.buffer/(110*cos(radians(j)))) for i, j in zip(self.data.longitude, self.data.latitude)]
        else:
            print('Getting school geometry object...')
            self.data['geometry'] = self.data['school_location']

        return gp.GeoDataFrame(self.data, crs='epsg:4326')

"""LOAD DEPENDENCIES"""
import geopandas as gp
import shapely
from urllib.request import urlopen
shapely.speedups.disable()

from feature_engineering import configs

"""COUNTRY CLASS"""
class Country:

    def __init__(self, country_code):
        if len(country_code)==3:
            self.country_code =country_code
        else:
            raise ValueError('Input country code should be in ISO 3166-1 alpha-3 format!')

        self.set_country_geometry()


    """sets geodata and country_name attributes"""
    def set_country_geometry(self):
        try:
            countries = gp.read_file(configs.WD + 'data/geodata/countries.json') ### Please edit the wd to your countries.json file dir!
        except:
            with urlopen('https://raw.githubusercontent.com/johan/world.geo.json/master/countries.geo.json') as response:
                countries = gp.read_file(response)
        
        if self.country_code.upper() in countries.id.values:
            self.geodata = countries[countries.id == self.country_code.upper()]
            self.country_name = self.geodata.name.values[0]
        else:
            raise ValueError('Country code not exist!')
        

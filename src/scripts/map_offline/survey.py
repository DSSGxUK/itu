
"""LOAD DEPENDENCIES"""
from bs4 import BeautifulSoup, SoupStrainer
import savReaderWriter as savr
import httplib2
from tqdm import tqdm
import geopandas as gp
import pandas as pd
import os


"""LOAD MODULES"""
from country import *
from data_gathering.opendata_utils import *
from feature_engineering import configs


"""SURVEY CLASS AS SUBCLASS OF COUNTRY"""
class Survey(Country):

    def __init__(self, country_code):
        super().__init__(country_code)
        self.available_countries = configs.AVAILABLE_COUNTRIES # manually controlled attribute keeps available country codes
        self.func_map = {i: i.upper() + '_Survey' for i in self.available_countries} # attribute to map country code to functions
        
        if (self.country_code.upper() + '_Survey') in self.func_map.values():
            self.data = eval(self.func_map[self.country_code] + '()').data
        else:
            self.data = None
            print('Survey data for ' + self.country_name + ' not exist! Continue without ground truth!')


"""CLASS THAT HOLDS SURVEY DATA FOR BRAZIL"""
class BRA_Survey(Survey):

    def __init__(self, wd = '../../../data/survey/Brazil/'):
        self.wd = wd ### Please edit the wd to your data folder!
        self.data = self.set_survey_data()


    """returns links for brazil enumeration area shape files"""
    def get_area_links(self):
        base_url = "https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_de_setores_censitarios__divisoes_intramunicipais/censo_2010/setores_censitarios_shp/"
        links=[]

        http = httplib2.Http()
        status, response = http.request(base_url)

        for link in BeautifulSoup(response, 'html.parser', parse_only=SoupStrainer('a')):
            if link.has_attr('href') and len(link['href'])==3:
                    status2, response2 = http.request(base_url+link['href'])
                    for link2 in BeautifulSoup(response2, 'html.parser', parse_only=SoupStrainer('a')):
                        if link2.has_attr('href') and link2['href'].endswith('_setores_censitarios.zip'):
                            print(link['href']+link2['href'])
                            links.append(link['href']+link2['href'])
        
        return base_url, links


    def set_survey_data(self):
        
        if os.path.exists(self.wd + 'survey_bra.csv'):
            print('Reading survey data for Brazil...')
            try:
                df_area = pd.read_csv(self.wd + "survey_bra.csv")
                df_area = df_area[df_area.geometry.isna()==False]
                gdf = df_to_gdf(df_area)
            except:
                raise RuntimeError('Unable to read survey data!')

        else:
            print('Downloading enumeration area shape files...')
            try:
                base_url, links = self.get_area_links()
                gdf_area = gp.GeoDataFrame()
                for link in tqdm(links):
                    gdf_area = gp.GeoDataFrame(pd.concat([gdf_area, gp.read_file(base_url+link)], ignore_index=True))
            except:
                raise RuntimeError('Unable to download enumeration area shape files!')
            
        
            # edit the CD_GEOCODI variable in order to match survey data and enumeration area data
            gdf_area.CD_GEOCODI = gdf_area.CD_GEOCODI.astype(str)

            # get survey data
            """ SURVEY DATA """
            print('Reading raw survey data for Brazil...')
            try:
                with savr.SavReader(self.wd + 'EA_2019.sav', ioUtf8 = True) as reader:
                    df_survey = pd.DataFrame(reader.all(), columns = reader.header)
            except:
                raise RuntimeError('Unable to read raw survey dataset!')
            
            # edit the CODSETOR variable in order to match survey data and enumeration area data
            df_survey.CODSETOR = df_survey.CODSETOR.astype(str)
            df_survey['CD_GEOCODI'] = [i[:-2] for i in df_survey.CODSETOR]

            # join areas to survey data
            print('Joining enumeration area geometries with survey data...')
            dff = df_survey.set_index('CD_GEOCODI').join(gdf_area.set_index('CD_GEOCODI')).reset_index()
            dff = dff[dff.geometry.isna()==False]
            gdf = gp.GeoDataFrame(dff, crs="EPSG:4326", geometry=dff.geometry)
            gdf = gdf[['A4A', 'geometry']]
            gdf.rename(columns = {'A4A': 'target'}, inplace = True)
            gdf.to_csv(self.wd + 'survey_bra.csv', index = False)
        
        return gdf


"""CLASS THAT HOLDS SURVEY DATA FOR THAILAND"""
class THA_Survey(Survey):

    def __init__(self, wd = '../../../data/survey/Thailand/'):
        self.wd = wd
        self.data = self.set_survey_data()

    
    def set_survey_data(self):

        if os.path.exists(self.wd + 'survey_tha.csv'):
            print('Reading survey data for Thailand...')
            try:
                survey_pro = pd.read_csv(self.wd + "survey_tha.csv")
                survey_pro = df_to_gdf(survey_pro)
            except:
                raise RuntimeError('Unable to read survey data!')

        else:

            # reading province shape files
            if os.path.exists('../../../data/geodata/tha_pro.csv'):
                print('Reading province data for Thailand...')
                try:
                    provinces = pd.read_csv('../../../data/geodata/tha_pro.csv')
                    provinces = df_to_gdf(provinces)
                except:
                    raise RuntimeError('Unable to read province data!')
                    
            else:
                print('Downloading province data for Thailand...')
                try:
                    with urlopen('https://data.opendevelopmentmekong.net/th/dataset/8f3fa1b8-cb5c-48c8-9fd7-d3c213ea23db/resource/1559cee4-fedc-4330-be9c-d8cf3dd75015/download/tha_admbnda_adm1_rtsd_20190221.zip') as file:
                        provinces = gp.read_file(file)
                    provinces['ADM1_PCODE'] = [int(i[2:]) for i in provinces['ADM1_PCODE']]
                    provinces.rename(columns = {'ADM1_EN': 'name', 'ADM1_PCODE': 'CWT'}, inplace=True)
                    provinces = provinces[['CWT', 'name', 'geometry']]
                    provinces.to_csv(self.wd + '../../geodata/tha_pro.csv')
                except:
                    raise RuntimeError('Unable to download province data!')

            print('Reading raw survey data for Thailand...')
            try:
                survey =pd.read_csv(self.wd + 'Microdata ICTHTV 2562 REC01.csv')
                survey = survey[['CWT', 'H107']]
                survey['H107'].replace(' ', np.nan, inplace = True)
                survey.dropna(subset = ['H107'], inplace = True)
                target_dict = {'1': 1, '2': 0, '3': 0}
                survey['H107'] = survey['H107'].map(target_dict)
            except:
                raise RuntimeError('Unable to read raw survey data!')

            print('Joining province geometries with survey data...')
            survey_pro = survey.merge(provinces, how = 'inner')
            survey_pro = survey_pro[['H107', 'geometry']]
            survey_pro.rename(columns = {'H107': 'target'}, inplace = True)
            survey_pro.to_csv(self.wd + 'survey_tha.csv', index = False)

        return gp.GeoDataFrame(survey_pro, crs='epsg:4326')

class PHL_Survey(Survey):

    def __init__(self, wd = '../../../data/survey/Philippines/'):
        self.wd = wd
        self.data = self.set_survey_data()

    
    def set_survey_data(self):
        if os.path.exists(self.wd + 'survey_phl.csv'):
            print('Reading survey data for Philippines...')
            try:
                survey_brgy = pd.read_csv(self.wd + "survey_phl.csv")
                survey_brgy = df_to_gdf(survey_brgy)
            except:
                raise RuntimeError('Unable to read survey data!')

        else:

            # reading barangay shape files
            if os.path.exists('../../../data/geodata/phl_brgy'):
                print('Reading barangay shapefiles for Philippines...')
                try:
                    brgys = gp.read_file('../../../data/geodata/phl_brgy')
                    brgys[['prov', 'cit_mun', 'brgy']] = [[i.upper(), j.upper(), k.upper()] for i, j, k in zip(brgys.NAME_1, brgys.NAME_2, brgys.NAME_3)]
                    brgys = brgys[['prov', 'cit_mun', 'brgy', 'geometry']]
                except:
                    raise RuntimeError('Unable to read barangay shapefiles!')

            else:
                raise RuntimeError('Please download barangay shapefiles for Philippines from https://www.philgis.org/country-barangay/country-barangays-file/ ; unzip and name the folder as phl_brgy then locate it under geodata folder!')
            
            print('Reading individuals survey data for Philippines...')
            try:
                survey = pd.read_csv(self)
            except:
                raise RuntimeError('Unable to read individuals survey data!')
            
            print('Joining barrangay geometries with individuals survey data...')
            survey_brgy = survey.merge(brgys, on=['prov', 'cit_mun', 'brgy'])
            survey_brgy.rename(columns={'use_internet': 'target'}, inplace=True)
            survey_brgy.dropna(subset = ['target', 'geometry'], inplace=True)
            target_dict = {'YES': 1, 'NO': 0}
            survey_brgy.target = survey_brgy['target'].map(target_dict)
            survey_brgy_mean = survey_brgy.groupby(['prov', 'cit_mun', 'brgy']).mean()['target'].reset_index()
            survey_brgy = survey_brgy_mean.merge(brgys, on=['prov', 'cit_mun', 'brgy'])
            survey_brgy.to_csv(self.wd + 'survey_phl.csv', index = False)
        
        return gp.GeoDataFrame(survey_brgy, crs='epsg:4326')


            

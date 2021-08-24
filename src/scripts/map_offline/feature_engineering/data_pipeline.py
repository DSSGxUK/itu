
"""LOAD DEPENDENCIES"""
import pandas as pd
import geopandas as gp
import numpy as np
from tqdm import tqdm
import pickle
import os, stat
from sklearn.preprocessing import OneHotEncoder
from sklearn.neighbors import KDTree


"""LOAD MODULES"""
from feature_engineering import configs
from survey import *
from data_gathering.opendata import *


class FeatureEngineering():
    """
    Feature engineering
    """
    def __init__(self):
        #self.use_survey = configs.SURVEY_EXISTS
        self.data_dir = configs.WD + 'data/'
        self.country_code = configs.COUNTRY_CODE.lower()
        self.country = configs.COUNTRY.title()
        self.features = configs.FEATURES


        """SET SURVEY SCHOOL DATA"""
        if os.path.exists(self.data_dir + 'school_loc/school_data_' + self.country_code + '.csv'):
            print('Reading survey joined school data...')
            self.school_data = pd.read_csv(self.data_dir + 'school_loc/school_data_' + self.country_code + '.csv')
            self.school_data = df_to_gdf(self.school_data)
        else:
            self.school_data = School(self.country_code).data
            self.survey = Survey(self.country_code).data
            #if self.survey:
            if configs.SURVEY_AREAS == 'enumeration':
                self.school_data = self.join_survey_schools()
            elif configs.SURVEY_AREAS == 'tiles':
                self.school_data = self.join_by_kdtree()
            
            self.school_data.to_csv(self.data_dir + 'school_loc/school_data_' + self.country_code + '.csv', index= False)
        
        print('School dataset is initialized, length of the dataset is ' + str(len(self.school_data)) + '!')


    def load_feature(self, feature):
        """
        Load features and initialise within dataset
        :return: df - dataframe of feature
                 num, cat - numerical and categorical variables
                 sub_features - list of sub-features
        """
        if feature in ['satellite', 'facebook']:
            df = eval(feature.title() + 'Data("' + self.country_code + '", locations=self.school_data)').data
        else:
            df = eval(feature.title() + 'Data("' + self.country_code + '")').data

        # load data dictionary
        try:
            dic = pd.read_excel(self.data_dir + 'meta/' + feature + '_dict.xlsx', engine='openpyxl')
        except:
            raise RuntimeError('Please make sure that data dictionary for ' + feature + ' is in the directory as: ' + feature + '_dict.xlsx')

        # get feature names
        sub_features = []
        for row in dic.itertuples():
            if row.use == 'Y':
                sub_features.append(str(row.name))

        # identify variable type
        
        num = dic.loc[(dic.type == 'num') & (dic.use == 'Y'), 'name']
        cat = dic.loc[(dic.type == 'cat') & (dic.use == 'Y'), 'name']

        """
        Process numerical data
        :param df: dataframe of feature
        :param num: numerical variables
        :return: df - dataframe of feature
        """
        if df is not None:
            print('Processing numerical data...')
            for n in num:
                # replace missing values with median
                df[str(n)].fillna(df[str(n)].median())

            """
            Process categorical data
            :param df: dataframe of feature
            :param cat: categorical variables
            :return: df - dataframe of feature
            """
            print('Processing categorical data...')
            for c in cat:
                # drop missing values
                df[str(c)].fillna('missing')
                # one hot encoding of categorical values
                df[str(c)] = OneHotEncoder(df[str(c)])
        
        return df, sub_features


    def map_feature(self, feature):
        """
        Join schools to feature via the features geometry
        :param df: dataframe containing features to be added
        :param school_data: dataframe containing school data
        :param sub_features: list of sub-features
        :return: school_data - school dataframe with new features added
        """
        
        df, sub_features = self.load_feature(feature.lower())
        
        if feature.lower() == 'population':
            df = self.join_population(df)

        if 'source_school_id' in df:
            self.join_by_id(df)
            print(feature.title() + ' features added to the dataset!')
        else:
            self.join_by_kdtree(df, sub_features)
            print(feature.title() + ' features added to the dataset!')


    def get_centroids(self, df):

        if 'geometry' in df:
            # get centroids from polygon and point geometries
            print('Getting centroids...')
            if (df['geometry'][0].geom_type == 'Polygon') or (df['geometry'][0].geom_type == 'MultiPolygon'):
                try:
                    centroids = [i.centroid for i in df['geometry']]
                except RuntimeError:
                    print('Failed to get polygon centroids.')
                centroids = [[i.x, i.y] for i in centroids]
            elif df['geometry'][0].geom_type == 'Point':
                centroids = [[i.x, i.y] for i in df['geometry']]
        elif 'lon' in df:
            centroids = [[x, y] for x, y in zip(df['lon'], df['lat'])]
        elif 'longitude' in df:
            centroids = [[x, y] for x, y in zip(df['longitude'], df['latitude'])]

        return centroids

    
    def join_by_id(self, df):

        print('Mapping features to schools by source school id...')

        # if feature already mapped to school, merge dataframes
        try:
            self.school_data = self.school_data.merge(df, how='inner', on='source_school_id')
        except RuntimeError:
            print('Merge between dataframes using common school ID failed.')
        #print('Rows left after merge:', len(self.school_data.iterrows()))

    # construct kdtree of feature locations
    def build_tree(self, centroids):
        """
        Construct KD tree of locations to be queried by school locations
        :param centroids: locations corresponding to feature values
        :return: tree
        """
        print('Constructing KD tree..')
        tree = KDTree(centroids, leaf_size=2)
        with open(r"kdtreeOfCentroidsOfTiles.pickle", "wb") as output_file:
            pickle.dump(tree, output_file)

        return tree

    def join_by_kdtree(self, df, sub_features):
            print('Mapping features to schools by KDtree...')

            centroids = self.get_centroids(df)

            try:
                tree = self.build_tree(centroids)
            except RuntimeError:
                print('Could not construct location tree. "centroids" must be erroneous.')

            for feature in sub_features:
                self.school_data[feature] = np.zeros(len(self.school_data.source_school_id))

            print('Mapping closest tree nodes to the schools...')
            for row in tqdm(self.school_data.itertuples()):

                school_location_xy = [row.longitude, row.latitude]
                # query feature location tree with school location to match nearest neighbours
                try:
                    dist, ind = tree.query(np.array([school_location_xy]), k=1)
                except RuntimeError:
                    print('Failed to query location tree.')

                # set corresponding value of feature at this row in the school dataframe
                for feature in sub_features:
                    # get feature value at the index from tree query (i.e. feature value at nearest location to school)
                    value = df.loc[df.index == ind[0, 0]][feature][ind[0, 0]]

                    # for range features, set True for school being within range and False for out of range
                    if feature == 'range':
                        if value >= dist:
                            value = 1

                    self.school_data.at[row[0], feature] = value


    def join_population(self, df):
        """JOIN POPULATION"""
        if df is None:
            print('Reading joined population data...')
            df = pd.read_csv(self.data_dir + 'worldpop/school_agg_pop_' + self.country_code + '.csv')
        else:
            print('Joining population data...')
            df = gp.sjoin(self.school_data, df, how = 'inner', op = 'contains')
            df.drop(columns='index_right', inplace=True)
            df = df.groupby('source_school_id').sum().reset_index()
            df = df[['source_school_id', 'population']]
            df.to_csv(self.data_dir + 'worldpop/school_agg_pop_' + self.country_code + '.csv', index=False)

        return df


    def join_survey_schools(self):
        """
        Join schools to enumeration areas using buffer zones
        :param df: dataframe containing features to be added
        :param school_data: dataframe containing school data
        :param sub_features: list of sub-features
        :return: school_data - school dataframe with new features added
        """
        print('Joining survey data to schools...')
        school_survey = gp.sjoin(self.school_data, self.survey, how='inner', op='intersects')

        # DROP DUPLICATES
        print('Dropping multiple area joins...')
        for i in tqdm(list(set(school_survey.index[school_survey.index.duplicated()].tolist()))):
            index_area = school_survey.loc[i, 'index_right'].tolist()
            school_point = school_survey.loc[i, 'geometry'].tolist()[0].centroid
            area_dist = [i.distance(school_point) for i in self.survey.loc[index_area, 'geometry'].tolist()]
            min_index = index_area[area_dist.index(min(area_dist))]
            min_row = school_survey[(school_survey.index==i) & (school_survey.index_right==min_index)]
            school_survey.drop(index=i, inplace=True)
            school_survey = school_survey.append(min_row)
        
        school_survey.drop(columns='index_right', inplace=True)

        school_survey.reset_index(drop = True)

        return school_survey
    

    def set_training_data(self):
        for feature in configs.FEATURES:
            self.map_feature(feature)


    def get_opendata(self):
        feature_data = {}
        for feature in configs.FEATURES:
            if feature in ['satellite', 'facebook']:
                feature_data[feature] = eval(feature.title() + 'Data("' + self.country_code + '", locations=self.school_data)').data
            elif feature == 'population':
                pop_url, pop_name = get_pop_url(self.country_code, year= configs.POPULATION_DATASET_YEAR)

                print('Downloading population data...')
                try:
                    pop = gdal.Open(pop_url)
                except:
                    raise RuntimeError('Unable to download from ' + pop_url)

                feature_data[feature] = tif_to_gdf(pop)
            else:
                feature_data[feature] = eval(feature.title() + 'Data("' + self.country_code + '")').data
        
        return feature_data

    def get_population_connected(self):

        centroids = self.get_centroids(self.school_data)
        tree = self.build_tree(centroids)
        


    def save_training_set(self):
        """
        Save complete dataset
        :param school_data: Dataframe of all features mapped to schools
        """
        ts_dir = self.data_dir + 'training_sets/' + self.country + '/'

        lst = sorted(os.listdir(ts_dir))
        if len(lst) == 0:
            v_no = 1
        else:
            v_no = int(lst[-1][-7:-4]) +1

        v_no = str(v_no).zfill(3)

        path = ts_dir + 'training_set_v' + v_no + '.csv'
        with open(path, 'w') as out:
            self.school_data.to_csv(out, index= False)
            os.chmod(path, stat.S_IRWXO)
        print('Training dataset version ' + v_no + ' saved!')
        out.close()
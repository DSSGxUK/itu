
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from tqdm import tqdm
import geojson
import json
from shapely.geometry import Point
import requests
import logging
import gzip
import sys

"""POPULATION DATA"""

"""GET POPULATION COUNTS TIF FILE URL FROM WORLDPOP WEBSITE """
def get_pop_url(country_code: str, year: int) -> str:
    base_url = "https://data.worldpop.org/GIS/Population/Global_2000_2020_1km_UNadj/"
    url = f"{base_url}{year}/{country_code.upper()}/{country_code.lower()}_ppp_{year}_1km_Aggregated_UNadj.tif"
    name = f"{country_code.lower()}_ppp_{year}_1km_Aggregated_UNadj.tif"
    return url, name


"""SPEEDTEST DATA"""

"""GET SPEEDTEST DATA URL IN AWS DONWLOAD FORMAT """
def get_speedtest_url(service_type: str, year: int, q: int) -> str:

    def quarter_start(year: int, q: int) -> datetime:
        if not 1 <= q <= 4:
            raise ValueError("Quarter must be within [1, 2, 3, 4]")

        month = [1, 4, 7, 10]
        return datetime(year, month[q - 1], 1)

    dt = quarter_start(year, q)

    base_url = "https://ookla-open-data.s3.amazonaws.com/shapefiles/performance"
    url = f"{base_url}/type={service_type}/year={dt:%Y}/quarter={q}/{dt:%Y-%m-%d}_performance_{service_type}_tiles.zip"
    name = f"{dt:%Y-%m-%d}_performance_{service_type}_tiles.zip"
    return url, name


"""OPENCELL"""

"""GET OPENCELLID DATA URLS FOR COUNTRY FROM OPENCELLID WEBSITE"""
def get_opencell_url(country_code, token):
    url = "https://opencellid.org/downloads.php?token="+str(token)
    
    # find table
    html_content = requests.get(url).text 
    soup = BeautifulSoup(html_content, "lxml")
    table = soup.find("table", {'id':"regions"})
    
    # get header
    t_headers = []
    for th in table.find_all("th"):
        t_headers.append(th.text.replace('\n', ' ').strip())
    
    table_data = []
    # for all the rows of table
    for tr in table.tbody.find_all('tr'):
        t_row = {}
        
        for td, th in zip(tr.find_all("td"), t_headers):
            if 'Files' in th:
                t_row[th]=[]
                for a in td.find_all('a'):
                    t_row[th].append(a.get('href'))
            else:
                t_row[th] = td.text.replace('\n', '').strip()
        
        table_data.append(t_row)
    
    cell_dict = pd.DataFrame(table_data)

    ## get the links for the country code
    if country_code.upper()[:2] not in cell_dict['Country Code'].values:
        print('Invalid country code to get OpenCell Data!')
        sys.exit(1)
    else:
        links = cell_dict[cell_dict['Country Code']==country_code.upper()[:2]]['Files (grouped by MCC)'].values[0]

    return links


"""GET OPENCELLID DATA"""
def get_cell_data(country_code, token, wd):
    
    links = get_opencell_url(country_code, token)
    
    df_cell = pd.DataFrame()
    for link in links:
        response = requests.get(link, stream=True)
        temp_file = wd + country_code.lower()+'.csv.gz.tmp'

        totes_chunks = 0
        with open(temp_file, 'wb') as feed_file:
            for chunk in tqdm(response.iter_content(chunk_size=1024)):
                if chunk:
                    feed_file.write(chunk)
                    totes_chunks += 1024
        try:
            with gzip.open(temp_file, 'rt') as feed_data:
                df_cell = pd.concat([df_cell, pd.read_csv(feed_data)], ignore_index=True)
        except IOError:
            rate_limit = 'RATE_LIMITED'
            bad_token = 'INVALID_TOKEN'
            with open(temp_file, 'r') as eggs_erroneous:
                contents = eggs_erroneous.readline()
            if rate_limit in contents:
                logging.error("Feed did not update. You're rate-limited!")
            elif bad_token in contents:
                logging.error("API token rejected by Unwired Labs!!")
            else:
                logging.error("Non-specific error.  Details in %s", temp_file)
            raise
    
    return df_cell


"""OPENSTREETMAP SCHOOL LOCATIONS"""

def osm_to_json(country_code):    
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
    [out:json][timeout:600];
    // gather results
    area["ISO3166-1"="""+country_code.upper()[:2]+"""]->.searchArea;
    (
      // query part for: “amenity=school”
      node[amenity=school](area.searchArea);
      // way[amenity=school](area.searchArea);
      // rel[amenity=school](area.searchArea);
    );
    // get output
    out center;
    """

    r = requests.get(overpass_url, params={'data': overpass_query})
    if r.status_code != 200:
        print('failed')
    r.encoding = "utf-8"
    response = json.loads(r.text)
    return response['elements']


def get_osm_schools(country_code):
    elements = osm_to_json(country_code)
    ids_already_seen = set()
    tag = set()
    features = []
    geometry = None
    for elem in elements:
        try:
            if elem["id"] in ids_already_seen:
                continue
            ids_already_seen.add(elem["id"])
        except KeyError:
            print("Received corrupt data from Overpass (no id).")
        elem_type = elem.get("type")
        elem_tags = elem.get("tags")
        elem_tags['osm_type'] = elem_type
        for i in elem_tags.keys():
            if i not in tag:
                tag.add(i)
        elem_nodes = elem.get("nodes", None)
        elem_user = elem.get("user", None)
        elem_uid = elem.get("uid", None)
        elem_version = elem.get("version", None)
        if elem_nodes:
            elem_tags["nodes"] = elem_nodes
        if elem_user:
            elem_tags["user"] = elem_user
        if elem_uid:
            elem_tags["uid"] = elem_uid  
        if elem_version:
            elem_tags["version"] = elem_version  
        if elem_type == "node":
            # Create Point geometry
            geometry = geojson.Point((elem.get("lon"), elem.get("lat")))
            elem_tags['latitude']=elem.get("lat")
            elem_tags['longitude']=elem.get("lon")
        elif elem_type == "way" or elem_type == "relation":
            # Create Way center geometry
            geometry = geojson.Point((elem.get("center").get('lon'), elem.get("center").get('lat')))
            elem_tags['latitude']=elem.get("center").get('lat')
            elem_tags['longitude']=elem.get("center").get('lon')
        else:
            print("Received corrupt data from Overpass (invalid element).")

        if geometry:
            feature = geojson.Feature(
                id=elem["id"],
                geometry=geometry,
                properties=elem_tags
            )
            features.append(feature)

    data = geojson.FeatureCollection(features)
    df_schools = pd.DataFrame(data.features)
    len_df = len(df_schools)
    for i in tag:
        df_schools[i] = None
    
    print('Creating geodataframe of schools...')
    for i in tqdm(range(len_df)):
        school = df_schools.loc[i,]
        for j,k in zip(school.properties.keys(), school.properties.values()):
            try:
                df_schools.loc[i,j]=k
            except:
                break
        df_schools.loc[i,'geometry'] = Point(df_schools.loc[i,'geometry'].coordinates)
    df_schools.drop(columns='properties', inplace=True)
    df_schools.rename(columns={'id': 'source_school_id'}, inplace=True)

    return df_schools[['source_school_id', 'latitude', 'longitude']]

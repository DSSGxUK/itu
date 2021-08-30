
"""LOAD DEPENDENCIES"""
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi
from math import ceil
import time
import pandas as pd
import numpy as np



def fb_api_init(access_token, ad_account_id):
    print('Initializing the Facebook Marketing API...')
    api = FacebookAdsApi.init(access_token=access_token)
    my_account = AdAccount(ad_account_id)

    try:
        test = my_account.get_ads()
    except Exception as e:
        if e._api_error_code == 190:
            raise ValueError('Unable to initialize due to invalid or expired access token!')
        elif e._api_error_code == 100:
            raise ValueError('Unable to initialize due to invalid ad account id!')
        else:
            raise RuntimeError('Unable to initialize Facebook Marketing API, please check you credentials!')

    return api, my_account
        

"""function to get delivery estimate for a point with a specified radius returns tuple of estimate_dau, estimate_mau, estimate_ready"""
def point_delivery_estimate(my_account, lat, lon, radius):
    targeting_spec = {
    "geo_locations": {
    "custom_locations": [
        {'latitude': lat, 'longitude': lon, 'radius': radius, 'distance_unit': 'kilometer'},
    ],
    },
    }

    params = {'optimization_goal': 'REACH',
        'targeting_spec': targeting_spec,
    }

    delivery_estimate = my_account.get_delivery_estimate(params=params)
    return delivery_estimate[0]['estimate_dau'], delivery_estimate[0]['estimate_mau'], delivery_estimate[0]['estimate_ready']



def get_delivery_estimate(df, access_token, ad_account_id, call_limit, radius):
    api, my_account = fb_api_init(access_token, ad_account_id)

    no_chunks = ceil(len(df)/call_limit)

    if no_chunks == 1:
        print('Calling Facebook Ads API; collection will take few minutes!')
    else:
        print('Calling Facebook Ads API; collection will approximately take ' + str(no_chunks-1) + ' hour(s)!')

    estimate_dict = {'source_school_id': [], 'estimate_dau': [], 'estimate_mau': [], 'estimate_ready': []}

    for c_no, chunk in enumerate(np.array_split(df, no_chunks)):
        print('Getting facebook data for the chunk ' + str(c_no) + '...')
        
        for school in chunk.iterrows():
            out = [school[1].source_school_id]
            try:
                est = point_delivery_estimate(my_account, school[1].latitude, school[1].longitude, radius)
            except Exception as e:
                if e._api_error_code == 80004:
                    print('There have been too many calls!\nStopped at source school id: ' + str(school[1].source_school_id))
                    break
                est = [0, 0, False]
            
            [estimate_dict[j].append(i) for i,j in zip(out+list(est), estimate_dict.keys())]

        print('Done! Hold for one hour!\nTotal number of requests: ' + str(api._num_requests_attempted) + '\nNumber of remaining chunks: ' + str(no_chunks - c_no - 1))

        if (no_chunks - c_no - 1) != 0:
            time.sleep(3600)

    return pd.DataFrame(estimate_dict)
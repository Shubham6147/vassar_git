import os
import stsa #pip install git+https://github.com/pbrotoisworo/s1-tops-split-analyzer.git
from sentinelsat import SentinelAPI
import geopandas as gpd
import pandas as pd
from shapely.geometry import box




#start_date = '20230201'
#end_date = '20230315'
#aoi_filepath = 'C:/Users/shubh/Downloads/split_poly/trial_shp.shp'


def save_burst_number(aoi_filepath, start_date, end_date):


    # copernicus open access hub credentials 
    #username = 'arunbalaji'
    #password = 'rsgisaji'

    username = 'shubham6147'
    password = 'Shubham@4475'

    destination_location = os.path.basepath(aoi_filepath)

    
    api = SentinelAPI(username, password, 'https://scihub.copernicus.eu/dhus')

    aoi = gpd.read_file(aoi_filepath)

    geom =box(*aoi.total_bounds)

    #%% Query S1 SLC data
    s1_products = api.query(geom,
                         date=(start_date, end_date),
                         platformname = 'Sentinel-1',
                         producttype='SLC')

    s1_products.keys()

    #%% Extracting only specific information from the products
    title = []
    ingestion_date = []
    footprint = []
    quick_look = []
    product = []
    for i in s1_products.keys():
        title.append(s1_products[i]['title'])
        ingestion_date.append(s1_products[i]['ingestiondate'])
        footprint.append(s1_products[i]['footprint'])
        quick_look.append(s1_products[i]['link_icon'])
        product.append(s1_products[i]['link'])

    # Converting s1 slc data lists to df
    s1_df = pd.DataFrame(
    {'title': title,
     'ingestion_date': ingestion_date,
     'quicklook_link': quick_look,
     'product_link': product,
     'footprint': footprint
    })
    #%% Using stsa package to extract only bursts and saving
    iw1 = []
    iw2 = []
    iw3 = []

    s1 = stsa.TopsSplitAnalyzer()
    for i in s1_df['title']:
        s1.load_api(username,
                i,
                password,
                destination_location)


        all_bursts = s1.df

        overlaid = gpd.overlay(aoi,all_bursts,how='intersection')

        x = overlaid[(overlaid['subswath'] == 'IW1')]['burst'].values
        if len(x)==0: # no intersection
            iw1.append((0,0))    
        elif len(x)==1: # intersection with only 1 burst
            iw1.append((int(x[0]),int(x[0])))    
        else: # intersection with more than 1 burst
            iw1.append((int(min(x)),int(max(x))))


        y = overlaid[(overlaid['subswath'] == 'IW2')]['burst'].values
        if len(y)==0:
            iw2.append((0,0))
        elif len(y)==1:
            iw2.append((int(y[0]),int(y[0])))
        else:
            iw2.append((int(min(y)),int(max(y))))


        z = overlaid[(overlaid['subswath'] == 'IW3')]['burst'].values
        if len(z)==0:
            iw3.append((0,0))
        elif len(z)==1:
            iw3.append((int(z[0]),int(z[0])))
        else:
            iw3.append((int(min(z)),int(max(z))))


    #%% Converting the df to csv and saving it

    s1_df['IW1'] = iw1
    s1_df['IW2'] = iw2
    s1_df['IW3'] = iw3

    output_csv_path = aoi_filepath[:-4] + '.csv'

    s1_df.to_csv(output_csv_path)




#save_burst_number(aoi_filepath, start_date, end_date)

from json import load
import pandas as pd
import geopandas as gpd
import rasterio as rio
from pystac_client import Client
import rasterio
from rasterstats.io import Raster
import numpy as np
import matplotlib.pyplot as plt



#Sentinel 2 cogs endpint
api_url = "https://earth-search.aws.element84.com/v1"
collection = "sentinel-2-l2a"


#Load geojson 
file_path = "C:/Users/shubh/Downloads/test_read_subset/aoi_geojson.geojson"
file_content = load(open(file_path))


shape = gpd.read_file(file_path)
geometry = shape.iloc[0]['geometry']


#Get Time range
timeRange = '2019-06-01/2019-08-01'

# query stac api
client = Client.open(api_url)

SentinelSearch = client.search(
    datetime = timeRange,
    collections=[collection],
    intersects = geometry,
    )

Sentinel_items = SentinelSearch.item_collection()


def series_from(item):
    #item_id = item.id
    item_dict = {   'item_id' : item.id,
                    'Date': item.properties['datetime'][0:10],
                    'R' : item.assets['red'].href,
                    'N' : item.assets['nir'].href,
                }
    
    return pd.Series(item_dict)


series = [series_from(item) for item in Sentinel_items]

all_data_df = pd.DataFrame(series)

all_data_df['Date'] = pd.to_datetime(all_data_df['Date'])

date_range_5days = pd.date_range(start = all_data_df.Date.min(), end = all_data_df.Date.max() + pd.DateOffset(5),freq ='5D')

date_range_5days_zip = zip(date_range_5days[:-1], date_range_5days[1:])

data_dict = []

for st_date, en_date in date_range_5days_zip:

    print( st_date, en_date)
    
    filtered_data = all_data_df[(all_data_df["Date"] >= st_date) & (all_data_df["Date"] < en_date)]

    Nir_band = []
    Red_band = []
    
    for index, row in filtered_data.iterrows():
        
        red_href = row['R']
        nir_href = row['N']

        with Raster(red_href) as raster_obj:

            shape = shape.to_crs(raster_obj.src.crs)
            geom_bounds = shape.iloc[0]['geometry'].bounds
            geom = shape.iloc[0]['geometry']
            
            
            raster_subset = raster_obj.read(bounds=geom_bounds) 
            polygon_mask = rasterio.features.geometry_mask(geometries=[geom],
                                                   out_shape=(raster_subset.shape[0], 
                                                              raster_subset.shape[1]),
                                                   transform=raster_subset.affine,
                                                   all_touched=False,
                                                   invert=True)

            Red_band.append(raster_subset.array * polygon_mask)

        with Raster(nir_href) as raster_obj:

            shape = shape.to_crs(raster_obj.src.crs)
            geom_bounds = shape.iloc[0]['geometry'].bounds
            geom = shape.iloc[0]['geometry']

            
            raster_subset = raster_obj.read(bounds=geom_bounds) 
            polygon_mask = rasterio.features.geometry_mask(geometries=[geom],
                                                   out_shape=(raster_subset.shape[0], 
                                                              raster_subset.shape[1]),
                                                   transform=raster_subset.affine,
                                                   all_touched=False,
                                                   invert=True)

            Nir_band.append(raster_subset.array * polygon_mask)

    Nir_band = np.dstack(Nir_band)
    Nir_band = np.rollaxis(Nir_band,-1)
    
    Red_band = np.dstack(Red_band)
    Red_band = np.rollaxis(Red_band,-1)
    
    NDVI = (Nir_band -  Red_band)/ (Nir_band +  Red_band)

    max_NDVI = NDVI.max(axis = 0)

    max_NDVI[max_NDVI > 1] = 1

    median_NDVI = np.nanmedian(max_NDVI)
    
    print(median_NDVI)

    png_path = 'C:/Users/shubh/Downloads/test_read_subset/mp/' + str(st_date)[:10] + '_ndvi.png'
    print(png_path)

    plt.imshow(max_NDVI, cmap = 'RdYlGn')
    plt.axis('off')
    plt.savefig(png_path, bbox_inches='tight')

    final_data = {str(st_date)[:10] : [ median_NDVI, png_path ]}
    
    data_dict.append(final_data)
    








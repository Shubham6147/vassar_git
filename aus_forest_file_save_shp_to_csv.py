import os
import rasterio as rio
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd
import glob
import fiona
from tqdm import tqdm
from multiprocessing import Pool


shp_file_list = glob.glob("D:/aus_v2/iwm_0.01/*.shp")
print(len(shp_file_list))

for shp_file in tqdm(shp_file_list):
    shp_gdf = gpd.read_file(shp_file)

    shp_gdf['cen_x'] = shp_gdf.centroid.x
    shp_gdf['cen_y'] = shp_gdf.centroid.y



    csv_file = shp_file[:-4] + '.csv'
    shp_df = pd.DataFrame(shp_gdf.drop('geometry', axis = 1))
    shp_df.to_csv(csv_file, index= False)

    #break
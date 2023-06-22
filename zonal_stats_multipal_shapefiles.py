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

raster_lulc = rio.open(r"D:\aus_v2\AUS_North_1_Dynamic_world_lulc_april_2023_mode.tif")
lulc_affine = raster_lulc.transform
lulc_band = raster_lulc.read(1)

raster_ele = rio.open(r"D:\aus_v2\AUS_North_1_elevation_alos_gee.tif")
ele_affine = raster_ele.transform
ele_band = raster_ele.read(1)

##def zonal_stats_all(shp_file):
##
##    shp_gdf = gpd.read_file(shp_file)
##
##    band_stats_lulc = zonal_stats(shp_file, r"D:\aus_v2\AUS_North_1_Dynamic_world_lulc_april_2023_mode.tif", stats='majority', nodata = 0)
##    shp_gdf['lulc'] = [stat['majority'] for stat in band_stats_lulc]
##
##    band_stats_ele = zonal_stats(shp_file, r"D:\aus_v2\AUS_North_1_elevation_alos_gee.tif", stats='mean', nodata = 0)
##    shp_gdf['elevation'] = [stat['mean'] for stat in band_stats_ele]
##
##    with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
##        shp_gdf.to_file(shp_file)
##
##
##with Pool(4) as pool:
##    print('pool_started')
##    pool.map(zonal_stats_all, shp_file_list)




for shp_file in tqdm(shp_file_list):
    shp_gdf = gpd.read_file(shp_file)


    band_stats_lulc = zonal_stats(shp_gdf, lulc_band, stats='majority', affine=lulc_affine, nodata = 0)
    shp_gdf['lulc'] = [stat['majority'] for stat in band_stats_lulc]

    band_stats_ele = zonal_stats(shp_gdf, ele_band, stats='mean', affine=ele_affine, nodata = 0)
    shp_gdf['elevation'] = [stat['mean'] for stat in band_stats_ele]

    with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
        shp_gdf.to_file(shp_file)

import os
import rasterio
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd
import glob
import numpy as np


input_ras = "F:/YM_yield/YM_paper_v2/YM_farm_paper_v2/paddy/YM_V2_all_indices_paddy_heading_rdvi.tif"
#field = ['NDVI', 'GNDVI', 'NDMI',  'MASAVI', 'OSAVI', 'CI_GREEN', 'CI_RED', 'MSR', 'RVI']
#'RDVI',
field = ['RDVI']


zones = "F:/YM_yield/YM_paper_v2/Yamunanagar_cleaned/Haryana_farm_boundaries_paddy_heading.shp"

zone = gpd.read_file(zones)

file_name = os.path.basename(input_ras)



# Open the raster dataset
with rasterio.open(input_ras,"r+") as src:
    src.nodata = 0
    # Get the number of bands in the dataset
    num_bands = src.count
    print(num_bands)
    zone = zone.to_crs(src.crs)
    affine = src.transform
    # Loop through each band
    for i in range(1, num_bands+1):
        print(i)
        # Get the band data as a numpy array
        band = src.read(i)
        #band[band == 0] = np.nan
        field_mean = field[i-1] +"_"+ 'mean'
        field_median = field[i-1] +"_"+ 'median'
        field_max = field[i-1] +"_"+ 'max'
        field_min = field[i-1] +"_"+ 'min'
        # Calculate zonal statistics for the current band
        band_stats = zonal_stats(zone, band, stats=['mean', 'median', 'max', 'min'], affine=affine, nodata = 0)
        # Add the statistics to the DataFrame as a new column
        zone[field_mean] = [stat['mean'] for stat in band_stats]
        zone[field_median] = [stat['median'] for stat in band_stats]
        zone[field_max] = [stat['max'] for stat in band_stats]
        zone[field_min] = [stat['min'] for stat in band_stats]

    src.close()

zone.to_file('F:/YM_yield/YM_paper_v2/Yamunanagar_cleaned/Haryana_farm_boundaries_paddy_heading.shp')

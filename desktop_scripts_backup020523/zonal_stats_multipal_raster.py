#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     15-02-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import os
import rasterio
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd
import glob

# Define the raster (e.g. NDVI_Timeseries)
input_ras_path = glob.glob("C:/Users/VassarGIS/Downloads/Mandal&Farms_boundary/avg_wetness/*.tif")

# Define the zones (e.g. polygons)
zones = r"C:\Users\VassarGIS\Downloads\Mandal&Farms_boundary\jag29_farms_simplify.shp"

out_shp_path = r"C:\Users\VassarGIS\Downloads\Mandal&Farms_boundary\jag29_farms_simplify_zonal.shp"

# Create an empty DataFrame to store the statistics
zone = gpd.read_file(zones)

if zone.crs is None:
    zone = zone.set_crs(default_crs)

# Transform to a difference CRS.


for input_ras in input_ras_path:
    file_name = os.path.basename(input_ras)
    # Open the raster dataset
    with rasterio.open(input_ras) as src:
        # Get the number of bands in the dataset
        num_bands = src.count
        print(num_bands)
        zone = zone.to_crs(src.crs)
        affine = src.transform
        # Loop through each band
        for i in range(1, num_bands+1):
            # Get the band data as a numpy array
            band = src.read(i)
            band[band != 1] = 0
            field = file_name[-10:] +"b_"+ str(i)
            # Calculate zonal statistics for the current band
            band_stats = zonal_stats(zone, band, stats='mean', affine=affine, nodata = 0)
            # Add the statistics to the DataFrame as a new column
            zone[field] = [stat['mean'] for stat in band_stats]

        src.close()

#zone.drop('geometry', axis=1, inplace= True)
#zone = pd.DataFrame(zone)
zone.to_file(out_shp_path)

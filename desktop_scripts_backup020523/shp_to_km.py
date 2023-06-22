#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     10-01-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import geopandas as gpd
import fiona
import glob
import os

fiona.supported_drivers['KML'] = 'rw'

out_path = 'F:/DEM_Extraction/KML_Con/'
shp_files = glob.glob('F:/DEM_Extraction/KML/*.shp')




for shp_file_path in shp_files:
    #shp_file = gpd.read_file("F:/DEM_Extraction/KML/grid_1.shp")
    shp_file = gpd.read_file(shp_file_path)
    output_file_name = os.path.basename(shp_file_path)[:-3] + "kml"

    output_file = out_path + output_file_name

    shp_file = shp_file.to_crs("EPSG:4326")

    shp_file = shp_file['geometry']

    shp_file.to_file(output_file, driver='KML')
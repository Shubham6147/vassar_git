
import rasterio as rio
import glob
import os
import numpy as np
import geopandas as gpd


image_list = glob.glob('/media/vassarml/HDD/shubham/fbd/max_con/*.tif')

grid_shp = gpd.read_file('/media/vassarml/HDD/shubham/fbd/grid_buf150m/grid_buf150m.shp')

for image_file in image_list:

    image_uuid = os.path.basename(image_file)[:36]

    filtered_grid = grid_shp[grid_shp['GRID_UUID'] == image_uuid]

    reduce_size = filtered_grid.buffer(-50)

    xmin, ymin, xmax, ymax = reduce_size.geometry.bounds

    out_file = '/media/vassarml/HDD/shubham/fbd/crop_img/' + os.path.basename(image_file)[:-4] + '_crop.tif'

    cmd = f'gdal_translate -projwin {xmin} {ymin} {xmax} {ymax} -of GTiff {image_file} {out_file}'

    print(cmd)

    os.system(cmd)

    break








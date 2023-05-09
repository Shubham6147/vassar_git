import os
import glob
import rasterio
import numpy as np


#---------function Block ------------
def write_raster(array, meta_data, output_file):
    
    new_dataset = rasterio.open(
        output_file,
        'w',
        driver='GTiff',
        height=meta_data['height'],
        width=meta_data['width'],
        count=array.shape[0],
        dtype=array.dtype,
        crs=meta_data['crs'],
        compress='LZW',
        transform=meta_data['transform'])
    new_dataset.write(array.astype(array.dtype))
    new_dataset.close()
    print('Output writing is done..', output_file)


def percentage_raster(input_raster, output_raster):
    src = rasterio.open(input_raster)
    meta_data = src.meta
    input_arr = src.read()
    output_arr = (np.sum(input_arr, axis = 0)) * 100 /input_arr.shape[0]
    write_raster(output_arr, meta_data, output_raster)

#----- Code Block ---------------
    
dirr = '/mnt/d/Tamilnadu_KTCC_water_annual/'

files = sorted(glob.glob(dirr+'*.tif'))

for file in files:
    output_file = file[-4] + "_percentage.tif"
    percentage_raster(file, output_file)
    
    

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     25-11-2022
# Copyright:   (c) VassarGIS 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import glob
import rasterio
import numpy as np

img_path = r"J:\New folder\change_ktcc_2021_noise_removed.tif"


src = rasterio.open(img_path)
arr = src.read()

constant_arr = arr.copy()
constant_arr[constant_arr <= 100] = 0

change_val_arr = arr.copy()
change_val_arr[change_val_arr > 100] = 0

change_val_arr_10 = change_val_arr + 10
change_val_arr_10[change_val_arr_10 > 100] = 100
change_val_arr_10[arr >= 100] = 0


change_val_arr_20 = change_val_arr + 20
change_val_arr_20[change_val_arr_20 >= 100] = 100
change_val_arr_20[arr >= 100] = 0

modi_change_10 = constant_arr + change_val_arr_10
modi_change_20 = constant_arr + change_val_arr_20

modi_change_10[arr == 100] = 100
modi_change_20[arr == 100] = 100


outFileName = r'J:\New folder\change_ktcc_2021_noise_removed_10inc.tif'

band = modi_change_10

with rasterio.open(img_path) as dataset:
	meta_data = dataset.meta
new_dataset = rasterio.open(
	outFileName,
	'w',
	driver='GTiff',
	height=meta_data['height'],
	width=meta_data['width'],
	count=band.shape[0],
	dtype=band.dtype,
	crs=meta_data['crs'],
	compress='LZW',
	transform=meta_data['transform'])
new_dataset.write(band.astype(band.dtype))

new_dataset.close()

print('Output writing is done..', outFileName)



outFileName = r'J:\New folder\change_ktcc_2021_noise_removed_20inc.tif'

band = modi_change_20

with rasterio.open(img_path) as dataset:
	meta_data = dataset.meta
new_dataset = rasterio.open(
	outFileName,
	'w',
	driver='GTiff',
	height=meta_data['height'],
	width=meta_data['width'],
	count=band.shape[0],
	dtype=band.dtype,
	crs=meta_data['crs'],
	compress='LZW',
	transform=meta_data['transform'])
new_dataset.write(band.astype(band.dtype))

new_dataset.close()

print('Output writing is done..', outFileName)

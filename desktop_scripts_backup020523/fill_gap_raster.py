#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     24-11-2022
# Copyright:   (c) VassarGIS 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import rasterio
import numpy as np
from scipy.signal import savgol_filter
import pandas as pd
import time
from osgeo import gdal, gdalconst
from osgeo import osr
import os


def consecutive(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

def fill_gap(arr):
    if sum(arr) != 0 :
        indexs = np.argwhere(arr == 0)
        gaps = consecutive(indexs[:,0])
        gaps_arr1 = []
        gaps_arr2 = []
        for gap in gaps:
            if 0 not in gap and len(arr)-1 not in gap and len(gap) > 0 and len(gap) < 10:
                gaps_arr1.append(gap)
            elif (0 in gap or len(arr)-1 in gap) and len(gap) < 10:
                gaps_arr2.append(gap)
        if len(gaps_arr1) > 0:
            for gap in gaps_arr1:
                if arr[min(gap)-1] == arr[max(gap)+1]:
                    arr[gap] = arr[min(gap)-1]
                else:
                    diff = arr[min(gap)-1] - arr[max(gap)+1]
                    add = diff/(len(gap)+1)
                    for i in range(len(gap)):
                        arr[gap[i]] = arr[min(gap)-1] - (i+1)*add
        if len(gaps_arr2) > 0:
            for gap in gaps_arr2:
                if 0 in gap:

                    diff = arr[max(gap)+1] - arr[max(gap)+3]
                    add = diff/2
                    for i in range(len(gap)):
                        arr[gap[i]] = arr[max(gap)+1] + (len(gap) - i)*add
                elif len(arr)-1 in gap:
                    diff = arr[min(gap)-1] - arr[min(gap)-3]
                    add = diff/2
                    for i in range(len(gap)):
                        arr[gap[i]] = arr[min(gap)-1] + (i+1)*add

        return arr
    else:
        return arr


image_path = "E:/ET_calculation/NRSC_170days/stack/stack.tif"
image_src = rasterio.open(image_path)
meta_data = image_src.meta

image_arr = image_src.read()
image_arr = np.nan_to_num(image_arr)
image_arr[image_arr > 10] = 0

modified_image = np.zeros(image_arr.shape)
print(modified_image.shape)
print(image_arr.shape[1])
print(image_arr.shape[2])

for i in range(image_arr.shape[1]):
    for j in range(image_arr.shape[2]):
        org_timeseries_pix = image_arr[:,i,j]
        #modified_timeseries_pix = fill_gap(org_timeseries_pix)
        #modified_image[:,i,j] = modified_timeseries_pix

print(modified_image.shape)

sum_modified = np.sum(modified_image, axis= 0)
print(sum_modified.shape)

modified_image = image_arr
outras = "E:/ET_calculation/NRSC_170days/stack/stack_cor.tif"

new_dataset = rasterio.open(
	outras,
	'w',
	driver='GTiff',
	height=meta_data['height'],
	width=meta_data['width'],
	count=modified_image.shape[0],
	crs=meta_data['crs'],
	dtype = modified_image.dtype,
    compress = 'LZW',
	transform=meta_data['transform'],
)

new_dataset.write(modified_image.astype(modified_image.dtype))
new_dataset.close()

##outras = "E:/ET_calculation/NRSC_170days/stack/stack_gap_fill_sum.tif"
##
##new_dataset = rasterio.open(
##	outras,
##	'w',
##	driver='GTiff',
##	height=meta_data['height'],
##	width=meta_data['width'],
##	count=1,
##	crs=meta_data['crs'],
##	dtype = sum_modified.dtype,
##    compress = 'LZW',
##	transform=meta_data['transform'],
##)
##
##new_dataset.write_band(1, sum_modified.astype(sum_modified.dtype))
##new_dataset.close()
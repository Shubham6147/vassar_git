#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     17-11-2022
# Copyright:   (c) VassarGIS 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy as np
import os
import rasterio as rio
import glob

print('project', 'season', 'count', 'sum', 'median', 'mean',)
for file in glob.glob("E:/ET_calculation/et_sum_100/2020_21/updated_ras/*.tif"):
    project_name =  os.path.basename(file).split("_")[0]
    image_arr = rio.open(file).read(1)
    image_arr[image_arr <= 0] = np.nan
    sum_val = np.nansum(image_arr)
    non_zero = np.count_nonzero(image_arr)
    nan_mean = np.nanmean(image_arr)
    nan_median = np.nanmedian(image_arr)
    q1 = np.nanquantile(image_arr , 0.25)
    q3 = np.nanquantile(image_arr , 0.75)

    season = "wet"
    if file.__contains__("mask_dry"):
        season = "dry"

    print(project_name, season, non_zero, sum_val, nan_mean, nan_median, q1, q3)


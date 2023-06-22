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

import rasterio
import numpy as np
import os, sys
import glob
global wetness_index
def soil_wetness(raster_path, output_path, thre_min, thre_max):

    data = rasterio.open(raster_path).read()
    sensitivity = thre_min - thre_max # -30 - -10

    vh_data = data[0,:,:].reshape((1, data.shape[1], data.shape[2]))

    wetness_index = ((thre_min - vh_data) / sensitivity) *100


    wetness_index[vh_data == 0] = 0
    wetness_index[wetness_index>100] = 100
    wetness_index[wetness_index<0] = 0

    wetness_index = np.round(wetness_index)

    wetness_index = np.reshape(wetness_index, (1, data.shape[1], data.shape[2]))

    #wetness_index = wetness_index + 1

    path_value = 'left'

    if 'right' in raster_path:
        path_value = 'right'

    print('Path',path_value)

    if path_value == 'left':
        mask_left = rasterio.open(r"F:\SRSPwetnessindex\mask\SRSP_Crop_mask_left.tif").read()
        wetness_index = wetness_index[:,:12009,:] * mask_left

    else:
        mask_right = rasterio.open(r"F:\SRSPwetnessindex\mask\SRSP_Crop_mask_right.tif").read()
        wetness_index = wetness_index * mask_right[:,:20561,:]

    print(wetness_index.shape)

    #wetness_index[wetness_index>100] = 100
    wetness_index = wetness_index.astype(np.byte)
    wetness_index[wetness_index == 0] = 125

    with rasterio.open(raster_path) as dataset:
        meta_data = dataset.meta

    new_dataset = rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=meta_data['height'],
        width=meta_data['width'],
        count=wetness_index.shape[0],
        dtype=np.byte,
        crs=meta_data['crs'],
        compress='DEFLATE',
        nodata = 125,
        transform=meta_data['transform']
    )
    new_dataset.write(wetness_index.astype(np.byte))
    new_dataset.close()

raster_files = glob.glob(r"F:\SRSPwetnessindex\*.tif")

for raster_path in raster_files:

    output_filename = os.path.basename(raster_path).replace("-","")

    output_path = 'F:/SRSPwetnessindex/output/' + output_filename
    thre_min= -3000
    thre_max= -1000
    if not os.path.exists(output_path):
        print(output_filename)
        soil_wetness(raster_path, output_path, thre_min, thre_max)
    #break
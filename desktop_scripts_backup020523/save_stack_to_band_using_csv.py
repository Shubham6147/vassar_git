#-------------------------------------------------------------------------------
# Name:        module2
# Purpose:
#
# Author:      VassarGIS
#
# Created:     28-03-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pandas as pd
import rasterio
import glob
import os
import numpy as np

for raster_path in glob.glob('F:/OD_Sen1_Wetness/mask_final/*.tif'):

    filename = os.path.basename(raster_path)
    year = filename.split("_")[-1][:-4]
    project =  filename.split("_")[1]
    csv_path = f"E:/OD_stack_wetness/{filename[:-4]}.csv"

    data = rasterio.open(raster_path).read()
    #data1 = rasterio.open(raster_path).read()
    date_df = pd.read_csv(csv_path)
    date_list = date_df['system:time_start'].to_list()

    for no_bands in range(data.shape[0]):

        arr = data[no_bands, :, :]

        with rasterio.open(raster_path) as dataset:
            meta_data = dataset.meta

        output_path_parent = f'F:/Odisha_data/wetness_index_3/{project}/{year}/kharif/'

        if not os.path.exists(output_path_parent):
            os.makedirs(output_path_parent)

        output_path = output_path_parent + project + "_wetness_"+ date_list[no_bands].replace("-","") + '.tif'

        new_dataset = rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=meta_data['height'],
            width=meta_data['width'],
            count= 1,
            dtype=np.byte,
            crs=meta_data['crs'],
            compress='DEFLATE',
            nodata = 0,
            transform=meta_data['transform']
        )
        new_dataset.write_band(1, arr.astype(np.byte))
        new_dataset.close()





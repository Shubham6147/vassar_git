import pandas as pd
import rasterio
import glob
import os
import numpy as np
from datetime import datetime


for raster_path in glob.glob('K:/haryana/Wheat_paddy/NDVI/*.tif'):

    filename = os.path.basename(raster_path)
    #year = filename.split("_")[-1][:-4]
    project =  filename.split("_")[-1][:-4]
    print(project)
    csv_path = f"K:/haryana/Wheat_paddy/NDVI/{filename[:-4]}.csv"

    data = rasterio.open(raster_path).read()
    #data1 = rasterio.open(raster_path).read()
    date_df = pd.read_csv(csv_path)
    date_list = [str(datetime.fromtimestamp(i/1000.0).date()) for i in date_df['system:time_start'].to_list()]


    str(datetime.fromtimestamp(i/1000.0).date())

    for no_bands in range(data.shape[0]):

        arr = data[no_bands, :, :]

        with rasterio.open(raster_path) as dataset:
            meta_data = dataset.meta

        output_path_parent = f'===========/{project}/2022_23/{project}_Irrigation_coverageRabbi'

        if not os.path.exists(output_path_parent):
            os.makedirs(output_path_parent)

        output_path = output_path_parent + project + "_"+ date_list[no_bands].replace("-","") + '.tif'
        #print(output_path)

        new_dataset = rasterio.open(
            output_path,
            'w',
            driver='GTiff',
            height=meta_data['height'],
            width=meta_data['width'],
            count= 1,
            dtype=arr.dtype,
            crs=meta_data['crs'],
            compress='DEFLATE',
            nodata = 0,
            transform=meta_data['transform']
        )
        new_dataset.write_band(1, arr)
        new_dataset.close()





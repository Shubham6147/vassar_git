import os
import glob
import rasterio
import numpy as np

import os
projects = ["annapurna", "indiramma", "ranganayaka", "lmd", "ns", "srsp", "syp", "singur", "mallanna"]



input_path = "E:/ET_calculation/multiplication_100/2020_21"
out_path = "E:/ET_calculation/et_sum_100/2020_21/"
yy_year = "2020_2021"

for season in ["dry", "wet"]:
    for project in projects:
        first_file = f"{input_path}/{project}_{yy_year}_year_ndvi_mask_{season}_0_et.tif"
        first_file_name = os.path.basename(first_file)
        outFileName = out_path + first_file_name[:-8] + "et_sum.tif"

        print(first_file)
        if not os.path.exists(outFileName):
            src = rasterio.open(first_file)
            meta_data = src.meta

            sum_image_np = np.zeros((1, src.height, src.width))

            for i in range(0,17):
                filename = f"{input_path}/{project}_{yy_year}_year_ndvi_mask_{season}_{i}_et.tif"
                src = rasterio.open(filename)
                arr = src.read()
                sum_image_np = sum_image_np + arr


            print("witting data")
            print(outFileName)
            band = sum_image_np

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
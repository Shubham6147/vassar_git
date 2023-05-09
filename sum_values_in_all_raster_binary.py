import os
import glob
import rasterio
import numpy as np

dirr = '/mnt/d/Tamilnadu_KTCC_water_annual/'

files = sorted(glob.glob(dirr+'*.tif'))

all_image_arr = []

for file in files :
    src = rasterio.open(file)
    arr = src.read()
    image_arr = arr[0,:,:]
    all_image_arr.append(image_arr)

all_image_np = np.array(all_image_arr)
water_arr = np.ma.masked_where(all_image_np > 0.55, all_image_np)

data = new_data = np.sum((~water_arr.mask).astype(int), axis = 0)
#all_image_np_sum = np.sum(water_arr,axis = 0)

#data = all_image_np_sum.data
new_data = data.reshape((1,data.shape[0], data.shape[1]))

with rasterio.open(fp=r'/mnt/d/Tamilnadu_KTCC_water_annual/water_body_sum_all.tif', mode='w',**src.meta) as dst:
    dst.write(new_data)

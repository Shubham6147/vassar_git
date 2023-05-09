import rasterio as rio 
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd


swir_files = glob.glob('/mnt/c/Users/shubh/Downloads/INDIRA_PROJECT_SWIR/*.tif')

swir_arr = np.zeros((len(swir_files),2818, 1971))

i = 0             
for image in swir_files:
    arr = rio.open(image).read(1)
    swir_arr[i,:,:] = arr
    i = i + 1

    
    
ndvi_files = glob.glob('/mnt/c/Users/shubh/Downloads/INDIRA_PROJECT_NDVI/*.tif')

ndvi_arr = np.zeros((len(swir_files),2818, 1971))

i = 0             
for image in ndvi_files:
    arr = rio.open(image).read(1)
    ndvi_arr[i,:,:] = arr/10000
    i = i + 1

ndvi_flat = ndvi_arr.flatten()
swir_flat = swir_arr.flatten()


df = pd.DataFrame({'ndvi': ndvi_flat , 'swir': swir_flat})

for i in range(-9, 11, 1):
    floting_val = i/10 
    print(floting_val , floting_val - 0.1)
    min_val = floting_val - 0.1
    df_filterd = df[df['ndvi'] < floting_val &  df['ndvi'] > min_val]

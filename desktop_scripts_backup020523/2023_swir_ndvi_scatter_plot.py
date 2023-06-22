import rasterio as rio
import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd
from scipy.stats import gaussian_kde


swir_files = glob.glob('F:/wetness_index/sen2/INDIRA_PROJECT_SWIR_Sentinel/*.tif')

swir_arr = np.zeros((len(swir_files),1500, 1500))

i = 0
for image in swir_files:
    arr = rio.open(image).read(1)/10000
    swir_arr[i,:,:] = (((1.0 - arr[4500:6000, 3000:4500])**2.0)/(2.0 * arr[4500:6000, 3000:4500]))
    i = i + 1



ndvi_files = glob.glob('F:/wetness_index/sen2/INDIRA_PROJECT_NDVI_Sentinel/*.tif')

#ndvi_arr = np.zeros((len(swir_files),2818, 1971))
ndvi_arr = np.zeros((len(swir_files),1500, 1500))
i = 0
for image in ndvi_files:
    arr = rio.open(image).read(1)
    ndvi_arr[i,:,:] = arr[4500:6000, 3000:4500]/10000
    i = i + 1

ndvi_flat = ndvi_arr.flatten()
swir_flat = swir_arr.flatten()


df = pd.DataFrame({'ndvi': ndvi_flat , 'swir': swir_flat})

df_cleaned_2 = pd.DataFrame()
final_ndvi = []
final_swir = []

for i in range(21, 101, 1):
    floting_val = i/100
    print(floting_val , floting_val - 0.01)
    min_val = floting_val - 0.1
    df_filterd = df[(df['ndvi'] < floting_val) &  (df['ndvi'] > min_val)]

    swir_max = df_filterd.swir.quantile(0.98)
    swir_min = df_filterd.swir.quantile(0.02)

    final_ndvi.append(min_val)
    final_ndvi.append(min_val)

    final_swir.append(swir_max)
    final_swir.append(swir_min)

    df_filterd_swir = df_filterd[(df_filterd['swir'] < swir_max) &  (df_filterd['swir'] > swir_min)]
    df_cleaned_2 = df_cleaned_2.append(df_filterd_swir)


df_cleaned = pd.DataFrame({'ndvi': final_ndvi , 'swir': final_swir})
#df_cleaned_2 = pd.concat(final, axis=0)

bins = [100,100]

x = df_cleaned_2['ndvi'].to_numpy()
y = df_cleaned_2['swir'].to_numpy()

hh, locx, locy = np.histogram2d(x, y,bins)


# Sort the points by density, so that the densest points are plotted last
#z = np.array([hh[np.argmax(a<=locx[1:]),np.argmax(b<=locy[1:])] for a,b in zip(x,y)])
#idx = z.argsort()
#x2, y2, z2 = x[idx], y[idx], z[idx]

plt.figure(1,figsize=(8,8)).clf()
s = plt.scatter(x, y)#, c=z2, cmap='jet', marker='.')

#print("calculating_z")
#z = gaussian_kde(xy)(xy)
#print("calculating_z done")

#scatter_plt = df_cleaned_2.plot.scatter(x='ndvi',y = 'swir', c= z, s= 50, cmp = 'jet')

plt.savefig('F:/wetness_index/sen2_scatter_plt_density_ndvi_gte20_final_i8.png')


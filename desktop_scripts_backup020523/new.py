

import pickle
import numpy as np
import rasterio

with open("C:/Users/VassarGIS/Desktop/POC_Crop/POC/POC/test", "rb") as fp:
    b = pickle.load(fp)


d = np.array(b)
dshape=d.shape

l2=[]
for m in range(dshape[1]):
    l1=[]
    for n in range(dshape[0]):
        l1.append(d[n][m])
    l2.append(l1)

arr = np.array(l2)
arr1=arr.reshape(84,1462,2730)

OutFile = 'C:/Users/VassarGIS/Desktop/POC_Crop/POC/POC/ras.tif'
raw_raster = 'C:/Users/VassarGIS/Desktop/POC_Crop/POC/POC/POC_NDVI_stack/poc_NDVI_stack_2016-05-09_2017-06-28.tif'

with rasterio.open(raw_raster) as dataset:
    meta_data = dataset.meta
    data = dataset.read()
    new_dataset = rasterio.open(
	OutFile,
	'w',
	driver='GTiff',
	height=meta_data['height'],
	width=meta_data['width'],
	count=dataset.count,
	dtype=data.dtype,
	crs=meta_data['crs'],
	compress='LZW',
	transform=meta_data['transform'])
    new_dataset.write(arr1.astype(data.dtype))
    new_dataset.close()
    print('Output writing is done..', OutFile)









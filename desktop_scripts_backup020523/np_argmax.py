import rasterio
import numpy as np 

file_path = "E:/tg_mitank/left/mosaic.tif"

image_src = rasterio.open(file_path)

image_arr = image_src.read()
print(image_arr.shape)

classes = np.argmax(image_arr, axis = 0)
print(classes.shape)

band = classes.astype(np.int8)

outFileName = "E:/tg_mitank/left/mosaic_classes.tif"
meta_data = image_src.meta
new_dataset = rasterio.open(
	outFileName,
	'w',
	driver='GTiff',
	height=meta_data['height'],
	width=meta_data['width'],
	count=1,
	dtype=band.dtype,
	crs=meta_data['crs'],
	compress='LZW',
	transform=meta_data['transform'])
new_dataset.write_band(1, band.astype(np.int8))

new_dataset.close()

print('Output writing is done..', outFileName)


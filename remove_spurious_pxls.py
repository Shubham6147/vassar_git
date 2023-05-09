import skimage
from skimage import measure
import numpy as np
import rasterio
import cv2
import glob
import os


def remove_pixels(input_mask):
	labels_mask = measure.label(input_mask.astype(np.byte))
	regions = measure.regionprops(labels_mask)
	print(len(regions))

	region_area = []
	for i in range(len(regions)):
		region_area.append(regions[i].area)
	print(len(region_area))
	print(max(region_area), min(region_area), np.mean(region_area))

	if len(regions) > 1:
		for i in range(len(regions)):
			rg = regions[i]
			area = region_area[i]
			if area <= 30:
				labels_mask[rg.coords[:,0], rg.coords[:,1]] = 0
	labels_mask[labels_mask!=0] = 1
	mask = labels_mask
	print(mask.shape)
	return(mask)


def process_mask(inMask):

    input_mask = np.rollaxis(inMask, 0, 3)

    temp_mask = input_mask.copy()
    input_mask[temp_mask == 1] = 0
    input_mask[temp_mask == 0] = 1

    mask = remove_pixels(input_mask)

    temp_mask = mask.copy()
    mask[temp_mask == 0] = 1
    mask[temp_mask == 1] = 0

    input_mask = mask.copy()

    mask = remove_pixels(input_mask)
    ##print('mask shape', mask.shape)

    temp_data = np.empty((1, inMask.shape[1], inMask.shape[2]))
    temp_data[0,:,:] = mask[:,:,0]

    segments = temp_data.copy()
    return segments


def extract_mask(inras, outras, value):
    ras = rasterio.open(inras).read()

    mask = np.zeros(ras.shape, dtype = np.byte)

    mask[ras == value] = 1
    mask_process = process_mask(mask)

    ras[mask_process == 1] = value

    with rasterio.open(inras) as dataset:
    	meta_data = dataset.meta
    new_dataset = rasterio.open(
    	outras,
    	'w',
    	driver='GTiff',
    	height=meta_data['height'],
    	width=meta_data['width'],
    	count=ras.shape[0],
    	crs=meta_data['crs'],
    	dtype = ras.dtype,
        compress = 'DEFLATE',
    	transform=meta_data['transform'],
    )
    new_dataset.write(ras.astype(ras.dtype))
    new_dataset.close()

##filelist = sorted(glob.glob('D:/hirakud/Hirakud/*.tif'))
##for i in range (len(filelist)):
##    file_path = filelist[i]
##    output_path = 'D:/hirakud/Hirakud/edit/' + os.path.basename(filelist[i])
##    extract_mask(file_path, output_path, 1)
##    print('done')
years = ['1819']
parts = ['kharif']
codes = [0, 1,2,3,6,8]
for y in years:
    for p in parts:
        for c in range(1, 840):
            if c == 1:
##                data = 'E:/Sentinel_1_SLC/Scene8/Processing/pca_' + y + '_' + p +'_thematic_final.img'
                data = 'D:/SWISS_RE/21-0161_DTM_DEM/21-0161_DTM_4326_reclass.tif'
            else:
##                data = 'E:/Sentinel_1_SLC/Scene8/Processing/smoothed/pca_' + y + '_' + p +'_thematic_final_' + str(codes[c-1]) + '.img'
                data = 'D:/SWISS_RE/21-0161_DTM_DEM/DTM_reclass_smooth/21-0161_DTM_4326_reclass_' + str(c-1) + '.tif'
            print(data)
##            op = 'E:/Sentinel_1_SLC/Scene8/Processing/pca_' + y + '_' + p +'_thematic_final_' + str(codes[c]) + '.img'
            op = 'D:/SWISS_RE/21-0161_DTM_DEM/DTM_reclass_smooth/21-0161_DTM_4326_reclass_' + str(c) + '.tif'
            extract_mask(data, op, c)
            print('code = ', c)



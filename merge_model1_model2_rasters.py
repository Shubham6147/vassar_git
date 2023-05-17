import rasterio as rio
import glob
import os
import numpy as np

image_list = glob.glob('D:/mncfc/*.tif')

nemelist = [os.path.basename(x)[:-10] for x in image_list ]

unique_names = list(set(nemelist))


#---------function Block ------------
def write_raster(array, meta_data, output_file):

    new_dataset = rio.open(
        output_file,
        'w',
        driver='GTiff',
        height=meta_data['height'],
        width=meta_data['width'],
        count= 1,
        dtype=array.dtype,
        crs=meta_data['crs'],
        compress='LZW',
        transform=meta_data['transform'])

    new_dataset.write_band(1,array)
    new_dataset.close()
    print('Output writing is done..', output_file)




for unique_name in sorted(unique_names):

    files = glob.glob(f'D:/mncfc/{unique_name}*.tif')

    im_src = rio.open(files[0])
    im_arr = im_src.read(1)


    arr = np.zeros((len(files), im_arr.shape[0], im_arr.shape[1] ))

    for file in files:
        i = 0
        img_arr = rio.open(file).read(1)
        arr[i,:,:] = img_arr
        i = i+1

    arr[arr < 25] = 0
    arr[arr >= 25] = 1


    arr_sum = arr.sum(axis = 0)
    arr_sum[arr_sum>1] = 1


    output_file = files[0][:-10] + 'sum.tif'
    write_raster(arr_sum, im_src.meta, output_file)














































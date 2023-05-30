import rasterio as rio
import glob
import os
import numpy as np

image_list = glob.glob('F:/wb_galsi_preds_sub/*.tif')

nemelist = [os.path.basename(x)[:8] for x in image_list ]

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



#print(unique_names)

#unique_names =['F45D1113']

for unique_name in sorted(unique_names):

    files = glob.glob(f'F:/wb_galsi_preds_sub/{unique_name}*.tif')

    im_src = rio.open(files[0])
    im_arr_1 = im_src.read(1)

    arr = np.zeros((len(files), im_arr_1.shape[0], im_arr_1.shape[1] ))

    i = 0

    for ras_file in files:

        img_arr = rio.open(ras_file).read(1)

        img_arr[img_arr < 25] = 0
        img_arr[img_arr >= 25] = 1

        arr[i,:,:] = img_arr.copy()
        i = i + 1



    arr_sum = np.sum(arr, axis = 0)
    arr_sum[arr_sum >= 1] = 1


    output_file = 'F:/wb_galsi_preds_sub/Max_2_com/' + os.path.basename(files[0])[:-12] + '_sum.tif'
    print(output_file)
    write_raster(arr_sum, im_src.meta, output_file)














































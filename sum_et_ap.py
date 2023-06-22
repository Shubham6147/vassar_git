import rasterio as rio
import numpy as np

#---------function Block ------------
def write_raster(array, meta_data, output_file):

    new_dataset = rio.open(
        output_file,
        'w',
        driver='GTiff',
        height=meta_data['height'],
        width=meta_data['width'],
        count= array.shape[0],
        dtype=array.dtype,
        crs=meta_data['crs'],
        compress='LZW',
        transform=meta_data['transform'])

    new_dataset.write(array)
    new_dataset.close()
    print('Output writing is done..', output_file)



img_src = rio.open('F:/AP_ET/NDVI_musi/NDVI_cor/ndvi_cor/mask_musi_ndvi_cor_85_sep_april_cor.tif')
mask_ras = rio.open('F:/AP_ET/NDVI_musi/masks/crop_sep_april.tif').read(1)[:6583, :]

img_arr = img_src.read()
#img_arr = np.rollaxis(img_arr, 0, 3)

img_mask = np.zeros(img_arr.shape)


for i in range(0,img_arr.shape[0]):
    img_mask[i,:,:] = img_arr[i,:,:] * mask_ras


meta_data = img_src.meta
output_file = 'F:/AP_ET/NDVI_musi/NDVI_cor/mask_musi_ndvi_cor_85_sep_april.tif'
write_raster(img_mask, meta_data, output_file)


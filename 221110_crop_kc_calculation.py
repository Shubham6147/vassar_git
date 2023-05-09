import rasterio 
import rasterio as rio
import numpy as np

filename = "/mnt/d/NDVI_cor/annapurna_2020_2021_year_ndvi_mask_dry_cor_85.tif"
image = rio.open(filename)
image_arr = image.read()

wet = filename.__contains__("wet")

band_count = image_arr.shape[0]

def incremental(start,diff,intr):
    if intr != -1:
        yield start
        yield from incremental(start + diff,diff,intr-1)

def write_raster(array, input_file, output_file, patch_size = 500):
    ##    OutFile = OutFile + os.path.basename(tif_files[i])[16:-4] + '.tif'
    with rasterio.open(input_file) as src:
        meta_data = src.meta
    
    profile = {'driver':'GTiff',
        'height' : meta_data['height'],
        'width' : meta_data['width'],
        'count': array.shape[0],
        'dtype' : array.dtype,
        'crs' : meta_data['crs'],
        'compress' : 'LZW',
        'transform': meta_data['transform']}
    
    with rasterio.open(output_file, 'w', **profile) as dst:
        
        for i in range((src.shape[0] // patch_size) + 1):
            for j in range((src.shape[1] // patch_size) + 1):
                # define the pixels to read (and write) with rasterio windows reading
                col_off = j * patch_size
                row_off = i * patch_size
                width = min(patch_size, src.shape[1] - j * patch_size)
                height = min(patch_size, src.shape[0] - i * patch_size)
                window = rasterio.windows.Window(col_off, row_off, width, height)
                
                dst.write(array[:, row_off:row_off + height, col_off:col_off + width], window=window)

    print('Output writing is done..', output_file)
        

b = np.zeros((0,image_arr.shape[1],image_arr.shape[2]))
for i in range(0,band_count-1):
    diff = (image_arr[i+1] -  image_arr[i])/9
    a = incremental(image_arr[i],diff,9)
    list_a = list(a)
    a_arr = np.asarray(list_a)
    print(a_arr.shape)
    b = np.vstack((b, a_arr))

if wet :
    b = (1.9 * b)/10000 - 0.11
else:
    b = (1.31 * b)/10000 - 0.027
    
write_raster(b,filename, filename[:-4] + "_interpolated_KC.tif", patch_size = 100)

import glob
import os
import numpy as np

def Mosaic_raster(date, output):
    os.system('gdalbuildvrt F:/odisha_wsa/mosaic.vrt F:/KTCC/pred/*' + date + '*.tif')
    os.system('gdalwarp -r near -multi -wo "NUM_THREADS=ALL_CPUS" -co "COMPRESS=DEFLATE" -co "BIGTIFF=YES" F:/odisha_wsa/mosaic.vrt ' + output)
    os.remove('F:/odisha_wsa/mosaic.vrt')

raster_list = glob.glob('F:/KTCC/pred/*.tif')

outPath = 'F:/KTCC/mosaic/'
if not os.path.exists(outPath):
    os.makedirs(outPath)
date_list = []
for raster_path in raster_list:
    date = os.path.basename(raster_path)[28:38]
    date_list.append(date)
    print(date)
np_arr = np.array(date_list)
unique_date = np.unique(np_arr)
for date in unique_date:
    print(date)
    if date_list.count(date) > 1:
       filter_list = list(filter(lambda x: date in x, raster_list))
       print(filter_list)
       outMosaic1 = outPath + os.path.basename(filter_list[0])[:38] +'.tif'
       if not os.path.exists(outMosaic1):
            Mosaic_raster(date, outMosaic1)
            print(outMosaic1)
    else:
        filter_list = list(filter(lambda x: date in x, raster_list))
        file = filter_list[0]
        filename = os.path.basename(filter_list[0])[:38] +'.tif'
        os.system('move ' + file + ' ' + outPath + filename)
import glob
import os 

tms2geotiff = glob.glob(r'F:\MNCF_AGRI_DEMO\grid_MP_tiles\*.tif')

for tms2geotiff_output in tms2geotiff:
    
    final_filepath = tms2geotiff_output[:-4] + '_0.5m.jp2'
    print(final_filepath)

    final_resolution = 0.5



    gdal_cmd = f'gdal_translate -tr {final_resolution} {final_resolution} {tms2geotiff_output} {final_filepath}'
    print(gdal_cmd)
    os.system(gdal_cmd)

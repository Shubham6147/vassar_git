input_vrt_path = r"D:\gee_merge\vassar_labs_koraput_2021\mosaic.vrt"

with open(input_vrt_path, "r") as r:
    lines = r.readlines()

gotcha = False                 # Just a flag to know if we catched the field
with open(input_vrt_path, "w") as w:
    band_count = 1
    for k in range(len(lines)):
        if 'VRTRasterBand dataType="Int16"' in lines[k]:
            print(lines[k])
            w.write(f"""    <VRTRasterBand dataType="Int16" band="{band_count}" subClass="VRTDerivedRasterBand">
    <PixelFunctionType>average</PixelFunctionType>
    <PixelFunctionLanguage>Python</PixelFunctionLanguage>
    <PixelFunctionCode>
	<![CDATA[
import numpy as np
def average(in_ar, out_ar, xoff, yoff, xsize, ysize, raster_xsize,raster_ysize, buf_radius, gt, **kwargs):
    x = np.ma.masked_greater(in_ar, 10000)
    out_ar[:] = np.ma.max(x, axis = 0, fill_value=0)
    mask = np.all(x.mask,axis = 0)
    out_ar[mask]=0
	]]>
	</PixelFunctionCode>
	""") 

            band_count += 1
        else:
            w.write(lines[k])
        
#gdalwarp -srcnodata 0.0 -dstnodata 0.0 --config GDAL_VRT_ENABLE_PYTHON YES -r near -multi -wo "NUM_THREADS=ALL_CPUS" -co "COMPRESS=LZW" -co "BIGTIFF=YES" mosaic.vrt mosaic.tif
#--config GDAL_VRT_ENABLE_PYTHON YES

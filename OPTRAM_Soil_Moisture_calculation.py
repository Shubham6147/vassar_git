import numpy as np
import rasterio
import sys, os
from osgeo import gdal

def save_raster(input_path, output_path, data):
	with rasterio.open(input_path) as dataset:
		meta_data = dataset.meta
	new_dataset = rasterio.open(
		output_path,
		'w',
		driver='GTiff',
		height=data.shape[1],
		width=data.shape[2],
		count=data.shape[0],
		dtype=np.float32,
		crs=meta_data['crs'],
		transform=meta_data['transform'],
	)
	new_dataset.write_band(1,data.astype(np.float32))
	new_dataset.close()


def process_OPTRAM_Landsat(NIR_Band, RED_Band, SWIR_Band, Output_SM_Path):
    
    NIR = rasterio.open(NIR_Band).read()
    RED = rasterio.open(RED_Band).read()
    SWIR = rasterio.open(SWIR_Band).read()

    STR = ((1.0 - SWIR)**2.0)/(2.0 * SWIR)
    STR[STR == np.inf] = 1
    
    NDVI = (NIR - RED)/(NIR + RED)

    vd_opt = 1.1
    vw_opt = 4.5
    id_opt = 0.2
    iw_opt = 10

    sd_opt = vd_opt - id_opt
    sw_opt = vw_opt - iw_opt

    STRdry = (id_opt + (sd_opt * NDVI))
    STRwet = (iw_opt + (sw_opt * NDVI))

    OPTRAM  = (STRdry - STR)/(STRdry - STRwet)*100
    print(OPTRAM.shape)
    OPTRAM[OPTRAM > 100] = 110
    OPTRAM[SWIR <= 0] = 0
    

    save_raster(NIR_Band, Output_SM_Path, OPTRAM)


def process_OPTRAM_Sentinel2(NIR_Band, RED_Band, SWIR_Band, Output_SM_Path):
    
    NIR = rasterio.open(NIR_Band).read()
    RED = rasterio.open(RED_Band).read()
    SWIR = rasterio.open(SWIR_Band).read()

    STR = ((1.0 - SWIR)**2.0)/(2.0 * SWIR)
    STR[STR == np.inf] = 1
    
    NDVI = (NIR - RED)/(NIR + RED)

    vd_opt = 1.1
    vw_opt = 4.5
    id_opt = 0.2
    iw_opt = 10

    sd_opt = vd_opt - id_opt
    sw_opt = vw_opt - iw_opt

    STRdry = (id_opt + (sd_opt * NDVI))
    STRwet = (iw_opt + (sw_opt * NDVI))

    OPTRAM  = (STRdry - STR)/(STRdry - STRwet)*100
    print(OPTRAM.shape)
    OPTRAM[OPTRAM > 100] = 110
    OPTRAM[SWIR <= 0] = 0
    

    save_raster(NIR_Band, Output_SM_Path, OPTRAM)
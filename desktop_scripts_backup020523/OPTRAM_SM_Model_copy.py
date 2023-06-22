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
	new_dataset.write(data.astype(np.float32))
	new_dataset.close()



def Compute_OPTRAM(NIR, RED, SWIR, OutSM):
    NIR_ = rasterio.open(NIR).read()
    SWIR_ = rasterio.open(SWIR).read()
    #print(SWIR_[500:502,500:502])
    RED_ = rasterio.open(RED).read()

    ##print(np.isnan(np.min(SWIR_)))
    ##print(np.max(SWIR_))
    NIR2 = NIR_ / 10000
    RED2 = RED_ / 10000
    SWIR2 = SWIR_ / 10000

    STR1 = ((1.0 - SWIR2)**2.0)/(2.0 * SWIR2)
    STR = STR1.copy()
    STR[STR1 == np.inf] = 1
##    STR[STR1 > 20] = 1
    print(np.min(NIR_))
    print(np.max(NIR_))
    print('==', np.min(RED_))
    print(np.max(RED_))
    NDVI = (NIR2 - RED2)/(NIR2 + RED2)
    NDVI = np.nan_to_num(NDVI)
    print(np.min(NDVI))
    print(np.max(NDVI))


##    DbS = 0 #Dry bare soil or intercept of dry edge
##    WsV = 2.8 #Water stressed vegetation
##
##    SbS = 1.5 #Saturated bare soil or intercept of wet edge
##    WwV = 15 #Well-watered vegetation
##
##    Sd = WsV - DbS #slope of dry edge
##    Sw = WwV - SbS #Slope of Wet edge
##
##    OPTRAM  = ((DbS + (Sd * NDVI) - STR)/((DbS-SbS) + ((Sd-Sw) * NDVI)))*100


    vd_opt = np.min(STR[NDVI>0.5]) #STR_full_Cover_min
    print('vd_opt: ', vd_opt)
    vw_opt = np.max(STR[NDVI>0.5]) #STR_full_Cover_max
    print('vw_opt: ', vw_opt)

    id_opt  = np.min(STR[(NDVI>0) & (NDVI<0.2)]) #STR_bare_Soil_min
    print('id_opt: ', id_opt)
    iw_opt = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.95) #STR_bare_Soil_max
    print('iw_opt: ', iw_opt)

    sd_opt = vd_opt - id_opt
    print('sd_opt: ', sd_opt)
    sw_opt = vw_opt - iw_opt
    print('sw_opt: ', sw_opt)

    OPTRAM  = ((id_opt + (sd_opt * NDVI) - STR1)/((id_opt-iw_opt) + ((sd_opt-sw_opt) * NDVI)))*100
                #(id + (sd * NDVI) - STR)/((id-iw) + ((sd-sw) * NDVI))
    print(OPTRAM.shape)

##    OPTRAM[STR1 > 15] = 110
    OPTRAM[OPTRAM > 100] = 110
    OPTRAM[OPTRAM < 0] = 0
    save_raster(NIR, OutSM, OPTRAM)


def Compute_OPTRAM_NDVI(NDVI_data, SWIR, OutSM):
    NDVI_ = rasterio.open(NDVI_data).read()
    SWIR_ = rasterio.open(SWIR).read()
    #print(SWIR_[500:502,500:502])
##    RED_ = rasterio.open(RED).read()

    ##print(np.isnan(np.min(SWIR_)))
    ##print(np.max(SWIR_))
    NDVI = NDVI_ / 10000
##    RED2 = RED_ / 10000
    SWIR2 = SWIR_ / 10000

    STR1 = ((1.0 - SWIR2)**2.0)/(2.0 * SWIR2)
    STR = STR1.copy()
    STR[STR1 == np.inf] = 1
##    STR[STR1 > 20] = 1
##    print(np.min(NIR_))
##    print(np.max(NIR_))
##    print('==', np.min(RED_))
##    print(np.max(RED_))
##    NDVI = (NIR2 - RED2)/(NIR2 + RED2)
    NDVI = np.nan_to_num(NDVI)
    print(np.min(NDVI))
    print(np.max(NDVI))


##    DbS = 0 #Dry bare soil or intercept of dry edge
##    WsV = 2.8 #Water stressed vegetation
##
##    SbS = 1.5 #Saturated bare soil or intercept of wet edge
##    WwV = 15 #Well-watered vegetation
##
##    Sd = WsV - DbS #slope of dry edge
##    Sw = WwV - SbS #Slope of Wet edge
##
##    OPTRAM  = ((DbS + (Sd * NDVI) - STR)/((DbS-SbS) + ((Sd-Sw) * NDVI)))*100


    vd_opt = np.quantile(STR[NDVI>0.5], 0.02) #STR_full_Cover_min
    print('vd_opt: ', vd_opt)
    vw_opt = np.quantile(STR[NDVI>0.5], 0.98) #STR_full_Cover_max
    print('vw_opt: ', vw_opt)

    id_opt  = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.02) #STR_bare_Soil_min
    print('id_opt: ', id_opt)
    iw_opt = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.98) #STR_bare_Soil_max
    print('iw_opt: ', iw_opt)

    sd_opt = vd_opt - id_opt
    print('sd_opt: ', sd_opt)
    sw_opt = vw_opt - iw_opt
    print('sw_opt: ', sw_opt)

    OPTRAM  = ((id_opt + (sd_opt * NDVI) - STR1)/((id_opt-iw_opt) + ((sd_opt-sw_opt) * NDVI)))*100
                #(id + (sd * NDVI) - STR)/((id-iw) + ((sd-sw) * NDVI))
    print(OPTRAM.shape)
##    OPTRAM[STR1 > 15] = 110
    OPTRAM[OPTRAM > 100] = 110
    OPTRAM[OPTRAM < 0] = 0
    save_raster(NDVI_data, OutSM, OPTRAM)


def Compute_OPTRAM_NDVI2(NDVI_data, SWIR, OutSM):
    NDVI_ = rasterio.open(NDVI_data).read()
    SWIR_ = rasterio.open(SWIR).read()
    #print(SWIR_[500:502,500:502])
##    RED_ = rasterio.open(RED).read()

    ##print(np.isnan(np.min(SWIR_)))
    ##print(np.max(SWIR_))
    NDVI = NDVI_ / 10000
##    RED2 = RED_ / 10000
    SWIR2 = SWIR_ / 10000

    STR1 = ((1.0 - SWIR2)**2.0)/(2.0 * SWIR2)
    STR = STR1.copy()
    STR[STR1 == np.inf] = 1
##    STR[STR1 > 20] = 1
##    print(np.min(NIR_))
##    print(np.max(NIR_))
##    print('==', np.min(RED_))
##    print(np.max(RED_))
##    NDVI = (NIR2 - RED2)/(NIR2 + RED2)
    NDVI = np.nan_to_num(NDVI)
    print(np.min(NDVI))
    print(np.max(NDVI))


##    DbS = 0 #Dry bare soil or intercept of dry edge
##    WsV = 2.8 #Water stressed vegetation
##
##    SbS = 1.5 #Saturated bare soil or intercept of wet edge
##    WwV = 15 #Well-watered vegetation
##
##    Sd = WsV - DbS #slope of dry edge
##    Sw = WwV - SbS #Slope of Wet edge
##
##    OPTRAM  = ((DbS + (Sd * NDVI) - STR)/((DbS-SbS) + ((Sd-Sw) * NDVI)))*100


    vd_opt = np.quantile(STR[NDVI>0.5], 0.02) #STR_full_Cover_min
    print('vd_opt: ', vd_opt)
    vw_opt = np.quantile(STR[NDVI>0.5], 0.98) #STR_full_Cover_max
    print('vw_opt: ', vw_opt)

    id_opt  = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.02) #STR_bare_Soil_min
    print('id_opt: ', id_opt)
    iw_opt = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.98) #STR_bare_Soil_max
    print('iw_opt: ', iw_opt)

    sd_opt = vd_opt - id_opt
    print('sd_opt: ', sd_opt)
    sw_opt = vw_opt - iw_opt
    print('sw_opt: ', sw_opt)

    STRdry = (id_opt + (sd_opt * NDVI))
    STRwet = (iw_opt + (sw_opt * NDVI))

    OPTRAM  = (STRdry - STR1)/(STRdry - STRwet)*100
                #(id + (sd * NDVI) - STR)/((id-iw) + ((sd-sw) * NDVI))
    print(OPTRAM.shape)
##    OPTRAM[STR1 > 15] = 110
    OPTRAM[OPTRAM > 100] = 110
    OPTRAM[OPTRAM < 0] = 0
    save_raster(NDVI_data, OutSM, OPTRAM)

def Compute_OPTRAM_stack(NDVI_band, SWIR_band, OutSM):

    NDVI_ = rasterio.open(NDVI_band).read()
    SWIR_ = rasterio.open(SWIR_band).read()

    OPTRAM_ = np.zeros((NDVI_.shape[0], NDVI_.shape[1], NDVI_.shape[2]), np.float32())
    for i in range(len(NDVI_)):


        NDVI = NDVI_[i,:,:] / 10000

        SWIR2 = SWIR_[i,:,:] / 10000

##        STR1 = ((1.0 - SWIR2)**2.0)/(2.0 * SWIR2)
        STR = SWIR2.copy()
        STR[STR == np.inf] = 1
        NDVI = np.nan_to_num(NDVI)
        print(np.min(NDVI))
        print(np.max(NDVI))

        vd_opt = 0.3143
        vw_opt = 0.083
        id_opt = 0.5711
        iw_opt = 0.0406


    ##    vd_opt = np.quantile(STR[NDVI>0.5], 0.02) #STR_full_Cover_min
        print('vd_opt: ', vd_opt)
    ##    vw_opt = np.quantile(STR[NDVI>0.5], 0.98) #STR_full_Cover_max
        print('vw_opt: ', vw_opt)

    ##    id_opt  = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.02) #STR_bare_Soil_min
        print('id_opt: ', id_opt)
    ##    iw_opt = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.98) #STR_bare_Soil_max
        print('iw_opt: ', iw_opt)

        sd_opt = vd_opt - id_opt
        print('sd_opt: ', sd_opt)
        sw_opt = vw_opt - iw_opt
        print('sw_opt: ', sw_opt)

        STRdry = (id_opt + (sd_opt * NDVI))
        STRwet = (iw_opt + (sw_opt * NDVI))

        OPTRAM  = (STRdry - STR)/(STRdry - STRwet)*100
                    #(id + (sd * NDVI) - STR)/((id-iw) + ((sd-sw) * NDVI))
        print(OPTRAM.shape)
    ##    OPTRAM[STR1 > 15] = 110
        OPTRAM[OPTRAM > 100] = 110
##        OPTRAM[OPTRAM < 0] = 0
        OPTRAM[SWIR2 <= 0] = 0
        OPTRAM_[i, :, :] = OPTRAM
    ##    OPTRAM = np.reshape(OPTRAM, (1, OPTRAM.shape[0], OPTRAM.shape[1]))
    save_raster(NDVI_band, OutSM, OPTRAM_)


def Compute_OPTRAM_using_stack(stack_data, NDVI_band, SWIR_band, OutSM):
    stack_ras = rasterio.open(stack_data).read()
    NDVI_ = stack_ras[NDVI_band -1, :, :]
    SWIR_ = stack_ras[SWIR_band -1, :, :]


    #print(SWIR_[500:502,500:502])
##    RED_ = rasterio.open(RED).read()

    ##print(np.isnan(np.min(SWIR_)))
    ##print(np.max(SWIR_))


    NDVI = NDVI_ / 10000
##    RED2 = RED_ / 10000
    SWIR2 = SWIR_ / 10000

    STR1 = ((1.0 - SWIR2)**2.0)/(2.0 * SWIR2)
    STR = SWIR2.copy()
    STR[STR1 == np.inf] = 1
##    STR[STR1 > 20] = 1
##    print(np.min(NIR_))
##    print(np.max(NIR_))
##    print('==', np.min(RED_))
##    print(np.max(RED_))
##    NDVI = (NIR2 - RED2)/(NIR2 + RED2)
    NDVI = np.nan_to_num(NDVI)
    print(np.min(NDVI))
    print(np.max(NDVI))


##    DbS = 0 #Dry bare soil or intercept of dry edge
##    WsV = 2.8 #Water stressed vegetation
##
##    SbS = 1.5 #Saturated bare soil or intercept of wet edge
##    WwV = 15 #Well-watered vegetation
##
##    Sd = WsV - DbS #slope of dry edge
##    Sw = WwV - SbS #Slope of Wet edge
##
##    OPTRAM  = ((DbS + (Sd * NDVI) - STR)/((DbS-SbS) + ((Sd-Sw) * NDVI)))*100

    vd_opt = 0.3143
    vw_opt = 0.083
    id_opt = 0.5711
    iw_opt = 0.0406

##    vd_opt = 1.2
##    vw_opt = 3
##    id_opt = 0.3
##    iw_opt = 10

##    vd_opt = np.quantile(STR[NDVI>0.5], 0.02) #STR_full_Cover_min
    print('vd_opt: ', vd_opt)
##    vw_opt = np.quantile(STR[NDVI>0.5], 0.98) #STR_full_Cover_max
    print('vw_opt: ', vw_opt)

##    id_opt  = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.02) #STR_bare_Soil_min
    print('id_opt: ', id_opt)
##    iw_opt = np.quantile(STR[(NDVI>0) & (NDVI<0.2)], 0.98) #STR_bare_Soil_max
    print('iw_opt: ', iw_opt)

    sd_opt = vd_opt - id_opt
    print('sd_opt: ', sd_opt)
    sw_opt = vw_opt - iw_opt
    print('sw_opt: ', sw_opt)

    STRdry = (id_opt + (sd_opt * NDVI))
    STRwet = (iw_opt + (sw_opt * NDVI))

    OPTRAM  = (STRdry - STR1)/(STRdry - STRwet)*100
                #(id + (sd * NDVI) - STR)/((id-iw) + ((sd-sw) * NDVI))
    print(OPTRAM.shape)
##    OPTRAM[STR1 > 15] = 110
    OPTRAM[OPTRAM > 100] = 110
    OPTRAM[OPTRAM < 0] = 0
    OPTRAM[SWIR2 <= 0] = 0
    OPTRAM = np.reshape(OPTRAM, (1, OPTRAM.shape[0], OPTRAM.shape[1]))
    save_raster(stack_data, OutSM, OPTRAM)




NDVI = "D:/ET_work/Test_data/OD/S2/New folder/OD_bbox_S2_NDVI_stack.img"
SWIR = "D:/ET_work/Test_data/OD/S2/New folder/OD_bbox_S2_SWIR_stack.img"
SM = "D:/ET_work/Test_data/OD/S2/New folder/OD_bbox_S2_NDVI_vs_SWIR_OPTRAM_SM_swir.img"
Compute_OPTRAM_stack(NDVI, SWIR, SM)
print("Done")

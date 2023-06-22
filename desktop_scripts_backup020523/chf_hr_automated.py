#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     04-04-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import geopandas as gpd
import pandas as pd
import rasterio as rio
import numpy as np
import os
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd
import glob
from datetime import datetime

gdf = gpd.read_file('F:/haryan_all_dist_chf/shp/Haryana_Village_final_newuuid_wgs84.shp')

#dist_list = list(gdf['DISTRICT_N'].unique()).sort()

dist_list = ['AMBALA', 'BHIWANI', 'CHARKHI DADRI', 'FARIDABAD', 'FATEHABAD', 'GURGAON', 'HISAR', 'JHAJJAR', 'JIND', 'KAITHAL',
            'KARNAL', 'KURUKSHETRA', 'MAHENDERGARH', 'MEWAT', 'PALWAL', 'PANCHKULA', 'PANIPAT', 'REWARI', 'ROHTAK', 'SIRSA', 'SONIPAT', 'YAMUNANAGAR']

dist_list = ['MEWAT', 'PALWAL', 'PANCHKULA', 'PANIPAT', 'REWARI', 'ROHTAK', 'SIRSA', 'SONIPAT', 'YAMUNANAGAR']


#dist_list = ['AMBALA', 'JIND', 'KAITHAL', 'KARNAL', 'KURUKSHETRA',]
#dist_list = ['KURUKSHETRA']

ndvi_path = 'F:/haryan_all_dist_chf/HR_Dist_CHF_Indices_stack/'
ndmi_path = 'F:/haryan_all_dist_chf/HR_Dist_CHF_Indices_stack/'
vh_path = 'F:/haryan_all_dist_chf/vh/'
crop_mask_p = 'F:/haryan_all_dist_chf/crop_mask/'

fapar_wheat_path = r"F:\haryan_all_dist_chf\fapar\paddy_fapar_clip_sum.tif"
fapar_wheat = rio.open(fapar_wheat_path)

fapar_affine = fapar_wheat.transform

fapar_arr = fapar_wheat.read(1)



for dist in dist_list:
    zone = gdf[gdf['d_name'] == dist.title()]
    print(len(zone))

    dist = dist.replace(" ","")

    wheat_mask = dist.lower() + '_rice.tif'
    #paddy_mask = dist.lower() + '_paddy.tif'

    crop_mask_path = crop_mask_p + wheat_mask
    crop_mask_arr =  rio.open(crop_mask_path).read(1)


    ndvi_max_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_NDVI_Max.tif'
    ndvi_mean_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_NDVI_Mean.tif'
    ndvi_sd_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_NDVI_SD.tif'

    ndmi_max_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_NDMI_Max.tif'
    ndmi_mean_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_NDMI_Mean.tif'
    ndmi_sd_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_NDMI_SD.tif'

    vh_max_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_vh_Max.tif'
    vh_sum_filename = f'HR_Dist_chf_2021-22_paddy_{dist}_vh_sum.tif'


    # All file paths

    ndvi_max_path = ndvi_path + ndvi_max_filename
    ndmi_max_path = ndmi_path + ndmi_max_filename

    ndvi_mean_path = ndvi_path + ndvi_mean_filename
    ndmi_mean_path = ndmi_path + ndmi_mean_filename

    ndvi_sd_path = ndvi_path + ndvi_sd_filename
    ndmi_sd_path = ndmi_path + ndmi_sd_filename

    vh_sum_path = vh_path + vh_sum_filename
    vh_max_path = vh_path + vh_max_filename


    #--------------------------------------------------

    #------------ COE calculation -----------------------
    ndvi_mean_arr =  rio.open(ndvi_mean_path).read(1)
    ndmi_mean_arr =  rio.open(ndmi_mean_path).read(1)

    ndvi_sd_arr =  rio.open(ndvi_sd_path).read(1)
    ndmi_sd_arr =  rio.open(ndmi_sd_path).read(1)

    ndvi_coe = ndvi_sd_arr/ndvi_mean_arr
    ndmi_coe = ndmi_sd_arr/ndmi_mean_arr

    ndmi_coe[ndmi_coe==np.inf] = 0
    ndvi_coe[ndvi_coe==np.inf] = 0

    coe_arr_inter = np.zeros((2,ndvi_coe.shape[0], ndvi_coe.shape[1]))

    coe_arr_inter[0,:,:] = ndvi_coe
    coe_arr_inter[1,:,:] = ndmi_coe

    coe_arr = np.max(coe_arr_inter,axis= 0)


    #-------------READING ARRAYS FOR MASKING -----------

    ndvi_max_arr =  rio.open(ndvi_max_path).read(1)
    ndmi_max_arr =  rio.open(ndmi_max_path).read(1)

    vh_max_arr =  rio.open(vh_max_path).read(1)
    vh_sum_arr =  rio.open(vh_sum_path).read(1)

    if dist == 'KARNAL':
        mask_ndvi_max_arr = ndvi_max_arr[:6158,:7935] * crop_mask_arr
        mask_ndmi_max_arr = ndmi_max_arr[:6158,:7935]* crop_mask_arr
        mask_vh_max_arr = vh_max_arr[:6158,:7935] * crop_mask_arr
        mask_vh_sum_arr = vh_sum_arr[:6158,:7935] * crop_mask_arr

    else:
        mask_ndvi_max_arr = ndvi_max_arr * crop_mask_arr
        mask_ndmi_max_arr = ndmi_max_arr * crop_mask_arr
        mask_vh_max_arr = vh_max_arr * crop_mask_arr
        mask_vh_sum_arr = vh_sum_arr * crop_mask_arr

    #------------------ Zonal Stats ------------------

    src = rio.open(ndvi_max_path)
    affine = src.transform



    band_stats = zonal_stats(zone, mask_ndvi_max_arr, stats='mean', affine=affine, nodata = 0)
    zone['ndvi_max'] = [stat['mean'] for stat in band_stats]

    band_stats = zonal_stats(zone, mask_ndmi_max_arr, stats='mean', affine=affine, nodata = 0)
    zone['ndmi_max'] = [stat['mean'] for stat in band_stats]

    band_stats = zonal_stats(zone, mask_vh_max_arr, stats='mean', affine=affine, nodata = 0)
    zone['vh_max'] = [stat['mean'] for stat in band_stats]

    band_stats = zonal_stats(zone, mask_vh_sum_arr, stats='mean', affine=affine, nodata = 0)
    zone['vh_sum'] = [stat['mean'] for stat in band_stats]

    band_stats = zonal_stats(zone, coe_arr, stats='mean', affine=affine, nodata = 0)
    zone['coe'] = [stat['mean'] for stat in band_stats]


    #------------------ Zonal Stats Fapar ------------------


    band_stats = zonal_stats(zone, fapar_arr, stats='mean', affine=fapar_affine, nodata = -3.4028234663852886e+38)
    zone['fapar_sum'] = [stat['mean'] for stat in band_stats]

    #--------------------------- CHF Calculation ---------------------------------
    # Min-Max Normalization
    df = zone[['ndvi_max', 'ndmi_max', 'vh_max', 'vh_sum', 'fapar_sum']]
    df_norm = (df-df.min())/(df.max()-df.min())

    # Max-Min Normalization
    df_coe = zone[['coe']]
    df_coe_norm = (df_coe.max()-df_coe)/(df_coe.max()-df_coe.min())

    df_norm = pd.concat((df_norm, df_coe_norm), 1)

    df_entropy = (df_norm/df_norm.sum()) * np.log(df_norm/df_norm.sum())
    entropy_each = - (df_entropy.sum()/ np.log(len(df_entropy)))

    weight = (1 - entropy_each) / (len(entropy_each) - entropy_each.sum())

    chf = weight * df_norm

    zone['CHF_VAL'] = chf.sum(axis = 1)

    out_filename= f'{dist}_chf_paddy_2021-22.shp'

    output_filepath = f'F:/haryan_all_dist_chf/output_chf/{out_filename}'

    zone.to_file(output_filepath)







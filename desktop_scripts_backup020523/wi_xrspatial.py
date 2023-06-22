#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Mar 13 16:54:42 2022

@author: santhosh
"""


from rasterstats import zonal_stats
from scipy.signal import savgol_filter
import statistics as s
import time
import glob
from scipy.ndimage.filters import uniform_filter1d

import os, os.path
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterio import features
from xrspatial import zonal_stats
import xarray as xr
import rasterio
import rioxarray

from affine import Affine


from scipy.signal import savgol_filter
import statistics as s
import time
import warnings
warnings.filterwarnings("ignore")

from scipy.ndimage.filters import uniform_filter1d
import os

from rasterio.enums import Resampling
from affine import Affine



import rasterio
import numpy as np
import time
import datetime
import os
import pandas as pd

import warnings
warnings.filterwarnings("ignore")



path = 'C:/Users/VassarGIS/Desktop/POC_Crop/APLIs_NDVI_Stack/2017may_onwards_APLIs_stack/'

csv_list = sorted(glob.glob(path+'*.csv'))
tif_list = sorted(glob.glob(path+'*.tif'))
#csv_list = csv_list[:1]
#tif_list = tif_list[:1]


def LayerDeStack(RasterStack, date_list, prefix, Outpath):
    # Read metadata of first file
    raster = rasterio.open(RasterStack).read()
    length = raster.shape[0]
    dateFormat ="%Y-%m-%d"

    for i in range(0, length):
        band = np.expand_dims(raster[i,:,:],0)
        #addDays=i * dayInterval
        date = date_list[i]
        #date = get_date(startDate, dateFormat, addDays)
        outFileName = os.path.join(Outpath, prefix + "_" + str(date) + '.tif')

        with rasterio.open(RasterStack) as dataset:
        	meta_data = dataset.meta
        new_dataset = rasterio.open(
        	outFileName,
        	'w',
        	driver='GTiff',
        	height=meta_data['height'],
        	width=meta_data['width'],
        	count=band.shape[0],
        	dtype=band.dtype,
        	crs=meta_data['crs'],
        	compress='LZW',
        	transform=meta_data['transform'])
        new_dataset.write(band.astype(band.dtype))
        new_dataset.close()
        print('Output writing is done..', outFileName)

def raster_writer(ref_raster, out_array, destination):
    shape = out_array.shape
    # print("file: ", ref_raster)
    with rasterio.open(ref_raster) as dataset:
    	meta_data = dataset.meta
    new_dataset = rasterio.open(
    	destination,
    	'w',
    	driver='GTiff',
        compress= "DEFLATE",
    	height=shape[1],
    	width=shape[2],
    	count=out_array.shape[0],
    	#count=len(arr),
        crs=meta_data['crs'],
    	dtype = out_array.dtype,
    	transform=Affine(8.983152841195214e-06, 0.0, t2,
               0.0, -8.983152841195214e-06, t5),
    )
    new_dataset.write(out_array.astype(out_array.dtype))
    new_dataset.close()

window_size = 3

def moving_avg(arr):
	return uniform_filter1d(arr, size=window_size)


def stats_df(zones_xarr, tif_file):
  tif = rioxarray.open_rasterio(tif_file)
  tif_b1 = tif.sel(band=1)
  #zones_xarr1 = zones_xarr.sel(band=1)
  mean_df = zonal_stats(zones_xarr, tif_b1, stats_funcs=['mean'])
  mean_df = mean_df.drop(len(shp),axis=0)
  return mean_df

def original(df,a):
  original = []
  for i in range(len(df)):
    x = df.iloc[i]
    x = x[a:]
    x = x.to_list()
    original.append(x)
  return original



#MVC maximum vaule composite
def MVC(original):
    resampled = []
    for i in range(0, len(original), 2):
      j = i+1
      if len(original)%2==0:
        length = len(original)
      else:
        length = len(original)-1
      if i<length:
        temp_max = max(original[i], original[j])
        resampled.append(temp_max)
    return resampled



#computing moving average with window size 3

def compute_MA(resampled):
    moving_average = []
    for j in range(len(resampled)):
      if j == len(resampled)-2: #condition for last second value in the list
        ma = (resampled[j]+resampled[j+1]+resampled[0])/3
        moving_average.append(ma)
      elif j == len(resampled)-1: #condition for the last value in the list
        ma = (resampled[j]+resampled[0]+resampled[1])/3
        moving_average.append(ma)
      else:
        ma = (resampled[j]+resampled[j+1]+resampled[j+2])/3
        moving_average.append(ma)
    return moving_average

#Imputing values using straight line formula
def straight_line_dropout_MA(resampled, moving_average):
    prev = next = 0
    j = -1
    thresh = abs(0.09*s.mean(resampled))
    while j < len(resampled)-2:
      j = j+1
      if resampled[j] < (moving_average[j]-200): #checking if the current value of list is less than the threshold w.r.t moving average list
        prev = j-1
        next = j+1
        while resampled[prev] < thresh and prev>0: #checking if the previous value is less than the threshold
            prev = prev-1
        while resampled[next] < thresh and next<len(resampled)-1: #likewise checking if the next value is less than the threshold
            next = next+1
        #calculating the straight line dropout
        slope = (resampled[next]-resampled[prev])/(next-prev)
        c = resampled[next] - (slope*next)
        resampled[j] = abs((slope*j) + c)
    return resampled


wnds=[7, 7]
orders=[2, 4]

def consecutive(data, stepsize=1):
	return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

def fill_gap(arr):
	if sum(arr) != 0 :
		indexs = np.argwhere(arr == 0)
		gaps = consecutive(indexs[:,0])
		gaps_arr1 = []
		gaps_arr2 = []
		for gap in gaps:
			if 0 not in gap and len(arr)-1 not in gap and len(gap) > 0 and len(gap) < 10:
				gaps_arr1.append(gap)
			elif 0 in gap or len(arr)-1 in gap and len(gap) < 10:
				gaps_arr2.append(gap)
		if len(gaps_arr1) > 0:
			for gap in gaps_arr1:
				if arr[min(gap)-1] == arr[max(gap)+1]:
					arr[gap] = arr[min(gap)-1]
				else:
					diff = arr[min(gap)-1] - arr[max(gap)+1]
					add = diff/(len(gap)+1)
					for i in range(len(gap)):
						arr[gap[i]] = arr[min(gap)-1] - (i+1)*add
		if len(gaps_arr2) > 0:
			for gap in gaps_arr2:
				if 0 in gap and max(gap)+3 < len(arr) and max(gap)+1 < len(arr):
					diff = arr[max(gap)+1] - arr[max(gap)+3]

					add = diff/2
					for i in range(len(gap)):
						arr[gap[i]] = arr[max(gap)+1] + (len(gap) - i)*add
				elif len(arr)-1 in gap:
					diff = arr[min(gap)-1] - arr[min(gap)-3]
					add = diff/2
					for i in range(len(gap)):
						arr[gap[i]] = arr[min(gap)-1] + (i+1)*add

		return arr
	else:
		return arr


def SG_Gapfill(arr):
    iter = 1
    if  sum(arr) == 0:
        return arr
    else:
        smoother_ts = savgol_filter(arr, window_length=wnds[0], polyorder=orders[1])
##            print(smoother_ts)
        diff = smoother_ts - arr
##            print(diff)
        sign = diff > 0
##            print(sign)

        W = 1 - np.abs(diff) / np.max(np.abs(diff)) * sign
##        print(W)
        arr[W<0.9] = 0
##        if iter == 1:
##            arr[W<0.9] = 0
##        else:
##            arr[(W>0.3) & (W<0.9)] = 0

        smooth_ts = fill_gap(arr)
    return smooth_ts





def SG_filter(SG_list):
  SG_smooth = []
  for i in range(len(SG_list)):
    x = SG_list[i]
    smooth = savgol_filter(x, 11, 5)
    SG_smooth.append(smooth)
  return SG_smooth

def Timeseries_Expand(Original_timeseries, Original_MVC_timeseries, Corrected_MVC_timeseries):
    #print('expanding timeserie...')
    Expanded_timeseries =np.zeros(len(Original_timeseries), float)

    count = 0
    for i in range(0, len(Original_timeseries), 2):
      j = i+1
      if len(Original_timeseries)%2==0:
        length = len(Original_timeseries)
      else:
        length = len(Original_timeseries)-1
      if i<length:
        if Original_MVC_timeseries[count] == Original_timeseries[i]:
            Expanded_timeseries[i] = Corrected_MVC_timeseries[count]
        elif Original_MVC_timeseries[count] == Original_timeseries[j]:
            Expanded_timeseries[j] = Corrected_MVC_timeseries[count]

        count += 1
    return Expanded_timeseries


def main_process(list):
    original_list = list
    final_list = []
    for i in range(len(original_list)):
        print(len(original_list[i]))
        MVC_pol = MVC(original_list[i])
        print('MVC',len(MVC_pol))
        moving_average = moving_avg(MVC_pol)
        print('moving_average',len(moving_average))
        MVC_dropout = straight_line_dropout_MA(MVC_pol, moving_average)
        print('MVC_dropout',len(MVC_dropout))
        fill_gap_arr = fill_gap(np.array(MVC_dropout))
        SG_gap_arr = SG_Gapfill(np.array(fill_gap_arr))
        smooth = savgol_filter(SG_gap_arr, 11, 5)
        print('smooth',len(smooth))
        #Expanded_timeseries = Timeseries_Expand(original_list[i], MVC_pol, smooth)
        #print('Expanded_timeseries',len(Expanded_timeseries))
        #Expanded_timeseries_gapfil = fill_gap(Expanded_timeseries)
        final_list.append(smooth)
    return final_list



for i in range(len(csv_list)):
    date_csv = pd.read_csv(csv_list[i])
    date_list = date_csv['prop']
    LIS_name = tif_list[i].split('/')[-1][:-4]
    LIS_name_destack = tif_list[i].split('/')[-1][:-37]
    outpath = 'C:/Users/VassarGIS/Desktop/POC_Crop/APLIs_NDVI_Stack/destack/' + LIS_name+'/'
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    LayerDeStack(tif_list[i],date_list, LIS_name_destack, outpath)

'''
    #upsample
    ds = rasterio.open(tif_list[i])
    transform = ds.meta['transform']
    t2 = transform[2]
    t5 = transform[5]
    upscale_factor = 10

    count =0
    tiflist1 = sorted(glob.glob(outpath+'/*.tif'))
    for tif1 in tiflist1:
        count = count+1
        name = tif1.split('/')[-1]
        dir1 = '/home/deepak-vlit/Desktop/POC/S2_APLIs/upsample/'+ LIS_name+'/'
        if not os.path.exists(dir1):
            os.makedirs(dir1)
        dest = dir1+name
        with rasterio.open(tif1) as dataset:

        # resample data to target shape
            data = dataset.read(
                out_shape=(
                    dataset.count,
                    int(dataset.height * upscale_factor),
                    int(dataset.width * upscale_factor)
                    ),
                resampling=Resampling.bilinear
                )

        # scale image transform
            transform = dataset.transform * dataset.transform.scale(
                (dataset.width / data.shape[-1]),
                (dataset.height / data.shape[-2])
                )

        raster_writer(tif1, data,dest)
        print("Just Completed file: ",count)





  #xrspatial

    time2s = time.time()

    shp_name = LIS_name[:-33]
    shp_path = '/home/deepak-vlit/Desktop/AP_LIs/AP_LI_Farms/Farm_shapefiles/'+shp_name+'_uuid_update.shp'
    shp = gpd.read_file(shp_path)
    #shp = gpd.read_file('/home/santhosh/Music/fbd/haryana/google_pred_shp/demo/demo1.shp')
    tif_list2 = sorted(glob.glob('/home/deepak-vlit/Desktop/POC/S2_APLIs/upsample/'+LIS_name+'/*.tif'))


    timeseries_mean = []
    k = 0
    for tif1 in tif_list2:
        mean_df = stats_df(shp, tif1)
        timeseries_mean.append(mean_df)
        k =k+1
        if k%10 == 0:
            print(k)

    final_mean = []
    for i in range(len(timeseries_mean)):
      mean = []
      for j in range(len(timeseries_mean[i])):
        mean.append(timeseries_mean[i][j]['mean'])
      final_mean.append(mean)



    mean_18_19 = final_mean
    #mean_19_20 = final_mean[73:146]
    #mean_20_21 = final_mean[146:219]
    #mean_21_present = final_mean[219:]

    time2e = time.time()

    print('time taken for zone stats computation:  ', (time2e-time2s)/60, ' mins')


    time3s = time.time()

    df_18_19 = shp.copy()
    #df_19_20 = shp.copy()
    #df_20_21 = shp.copy()
    #df_21_present = shp.copy()

    for i in range(len(mean_18_19)):
      df_18_19['mean_'+str(i+1)] = mean_18_19[i]


    df_18_19 = pd.DataFrame(df_18_19)

    ######################################################

    a = len(shp.columns)

    final_18_19 = main_process(df_18_19)
    final_18_19 =pd.DataFrame(final_18_19)
    final_18_19.columns = df_18_19.columns[a:]
    #final_18_19.to_csv('/home/santhosh/Music/fbd/ap/ap_final.csv',index=0)


    for i in range(len(tif_list2)):
        orig = pd.DataFrame()
        orig = shp[['LIS_UUID','LISff_uuid']]
        #orig['ndmi']=''
        orig['ndvi']=final_18_19['mean_{}'.format(i+1)]
        #orig['date']=''
        orig['date']=tif_list2[i][-14:-4]
        orig = pd.DataFrame(orig)
        orig.to_csv('/home/deepak-vlit/Desktop/POC/S2_APLIs/Sentinel_Filtered_ndvi_APLIs/test/{}.csv'.format(i),index =0)

    csvlist = sorted(glob.glob('/home/deepak-vlit/Desktop/POC/S2_APLIs/Sentinel_Filtered_ndvi_APLIs/test/*.csv'))
    df = pd.concat(map(pd.read_csv, csvlist), ignore_index=True)
    df['ndvi'] = df['ndvi']/10000
    final_outpath = '/home/deepak-vlit/Desktop/POC/S2_APLIs/Sentinel_Filtered_ndvi_APLIs/'+LIS_name+'/'
    if not os.path.exists(final_outpath):
        os.makedirs(final_outpath)
    df.to_csv(final_outpath+'/{}_ndvi.csv'.format(LIS_name),index=0)

    os.system('rm /home/deepak-vlit/Desktop/POC/S2_APLIs/Sentinel_Filtered_ndvi_APLIs/test/*')

 '''


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 31 14:00:49 2022

@author: deepak-vlit
"""
import rasterio as rio
import numpy as np
import pandas as pd
import geopandas as gpd
import os
import glob
import os, os.path
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
import statistics as s
import time
import glob
from scipy.ndimage.filters import uniform_filter1d

window_size = 3

def moving_avg(arr):
	return uniform_filter1d(arr, size=window_size)

import warnings
warnings.filterwarnings("ignore")

file_path= 'C:/Users/VassarGIS/Desktop/POC_Crop/APLIs_NDVI_Stack/Sentinel_2017may_onwards_APLIs_stack/vallampadu_NDVI_stack_2018-05-04_2019-06-28.tif'
tif_list = sorted(glob.glob(file_path+'*.tif'))

#for b in range(len(file_path)):
    #print(tif_list[b])

ds = rio.open(file_path).read()

shape = ds.shape
print('org_file shape :',shape)

list=[]

for x in range(shape[1]):
    for y in range(shape[2]):
        a=[]
        for z in range(shape[0]):
            a.append(ds[z,x,y])
        list.append(a)

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
				if 0 in gap:
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


final_list = main_process(list)



d = np.array(final_list)   # replace list by final list
dshape = d.shape

l2=[]
for m in range(dshape[1]):
    l1=[]
    for n in range(dshape[0]):
        l1.append(d[n][m])
    l2.append(l1)


arr = np.array(l2)
arr1 = arr.reshape(len(arr),shape[1],shape[2])
print('reshape :',arr1.shape)


raw_file = file_path
filename = 'test.tif'
outpath = 'C:/Users/VassarGIS/Desktop/POC_Crop/APLIs_NDVI_Stack/Filtered_Sentinel_APLIs_NDVI'
if not os.path.exists(outpath):
    os.makedirs(outpath)
outFileName = outpath+'/'+filename

with rio.open(raw_file) as dataset:
    meta_data = dataset.meta
    data = dataset.read()
    new_dataset = rio.open(
	outFileName,
	'w',
	driver='GTiff',
	height=meta_data['height'],
	width=meta_data['width'],
	count=len(arr),
	dtype=data.dtype,
	crs=meta_data['crs'],
	compress='LZW',
	transform=meta_data['transform'])
    new_dataset.write(arr1.astype(data.dtype))
    new_dataset.close()
    print('Output writing is done..', outFileName)


#for i in range(ds.shape[0]):
#    ndvi_array.append(ds[i][100][100])



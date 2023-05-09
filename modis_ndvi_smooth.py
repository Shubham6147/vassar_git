import os, os.path
import rasterio
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
from scipy.signal import savgol_filter
import statistics as s
import time
import glob
from scipy.ndimage.filters import uniform_filter1d
import os

#----------------------------------------------------------------------------
window_size = 3

def moving_avg(arr):
    return uniform_filter1d(arr, size=window_size)

import warnings
warnings.filterwarnings("ignore")

def stats_df(shp, tif_file):
  mean_df = zonal_stats(shp, tif_file, stats='mean')
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

wnds=[11, 7]
orders=[2, 4]
def savitzky_golay_filtering(arr):
    if  sum(arr) == 0 or arr[0] > 20000:
        return arr
    elif np.mean(arr, axis = 0) <= 2000:
        return arr
    else:
        interp_ts = pd.Series(arr)
        interp_ts = interp_ts.interpolate(method='linear', limit=14)
    ##    print(interp_ts)
        smooth_ts = interp_ts
        wnd, order = 111, 4
        F = 1e8
        W = None
        it = 0
        while True:
            smoother_ts = savgol_filter(smooth_ts, window_length=wnd, polyorder=order)
    ##            print(smoother_ts)
            diff = smoother_ts - interp_ts
    ##            print(diff)
            sign = diff > 0
    ##            print(sign)
            if W is None:
                W = 1 - np.abs(diff) / np.max(np.abs(diff)) * sign
                wnd, order = wnds[1], orders[1]
    ##                print(W)
            fitting_score = np.sum(np.abs(diff) * W)
            #print it, ' : ', fitting_score
            if fitting_score > F:
                break
            else:
                F = fitting_score
                it += 1
    ##                print('iteration', it)
    ##                print('F-score', F)
            smooth_ts = smoother_ts * sign + interp_ts * (1 - sign)
        return smooth_ts

    
def smooth_series(original_list):
    
    original_list = original_list.astype('int').to_list()
    MVC_pol = MVC(original_list)
    #print('MVC',len(MVC_pol))
    moving_average = moving_avg(MVC_pol)
    #print('moving_average',len(moving_average))
    MVC_dropout = straight_line_dropout_MA(MVC_pol, moving_average)
    #print('MVC_dropout',len(MVC_dropout))
    fill_gap_arr = fill_gap(np.array(MVC_dropout))
    SG_gap_arr = SG_Gapfill(np.array(fill_gap_arr))
    smooth = savitzky_golay_filtering(SG_gap_arr)
    #print('smooth',len(smooth))
    Expanded_timeseries = Timeseries_Expand(original_list, MVC_pol, smooth)
    #print('Expanded_timeseries',len(Expanded_timeseries))
    Expanded_timeseries_gapfil = fill_gap(Expanded_timeseries)
    return Expanded_timeseries_gapfil


#---------------------------------------------------------------------------

raster_path = ''
pred_output_path = ''

src = rasterio.open(raster_path)
meta_data = src.meta
wd = src.width
ht = src.height
widths = list(np.arange(0, wd, 50))
heights = list(np.arange(0, ht, 50))
if widths[-1] != wd: widths.append(wd)
if heights[-1] != ht: heights.append(ht)

print(widths)
print(heights)

pred_dataset = rasterio.open(
    pred_output_path,
    'w',
    driver='GTiff',
    height=ht,
    width=wd,
    count=920,
    dtype=np.ubyte,
    crs=meta_data['crs'],
    compress='DEFLATE',
    transform=meta_data['transform'],
    BIGTIFF='YES'
)

for w in range(len(widths)-1):
    for h in range(len(heights)-1):

        data = src.read(window=Window.from_slices((heights[h], heights[h+1]), (widths[w], widths[w+1])))
        
        new_data = np.zeros(data.shape)
        
        for i in range(data.shape[1]):
            for j in range(data.shape[2]):
                org_arr = data[:,i,j]
                if sum(org_arr) == 0:
                    new_data[:,i,j] = 0
                elif np.mean(org_arr) > 6500:
                     new_data[:,i,j] = org_arr
                
                elif np.mean(org_arr) < 0:
                     new_data[:,i,j] = org_arr
                
                else:
                    new_data[:,i,j] = smooth_series(org_arr)
        

        pred_dataset.write(new_data.astype('int'), window=Window.from_slices((heights[h], heights[h+1]), (widths[w], widths[w+1])))
pred_dataset.close()
src.close()

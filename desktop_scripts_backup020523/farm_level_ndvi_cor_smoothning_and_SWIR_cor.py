import sys, os
from skimage import io
from sklearn.cluster import KMeans
import numpy as np
from sklearn.decomposition import PCA
import pandas as pd
#from osgeo import gdal, gdalconst
#from osgeo import gdal, osr
#import Early_season_rice_detection_rule as Rice_detection_rule
import rasterio as rio

import math
import os, os.path
import geopandas as gpd
import matplotlib.pyplot as plt
from rasterstats import zonal_stats
from scipy.signal import savgol_filter
import statistics as s
import time
import glob
from scipy.ndimage.filters import uniform_filter1d
import os

window_size = 5

def moving_avg(arr):
	return uniform_filter1d(arr, size=window_size)

def raster_writer(ref_raster, out_array, destination):
    # print("file: ", ref_raster)
    with rio.open(ref_raster) as dataset:
    	meta_data = dataset.meta
    new_dataset = rio.open(
    	destination,
    	'w',
    	driver='GTiff',
        compress= "DEFLATE",
    	height=out_array.shape[1],
    	width=out_array.shape[2],
    	count=out_array.shape[0],
    	crs=meta_data['crs'],
    	dtype = out_array.dtype, #meta_data['dtype'],
    	transform=meta_data['transform'],
    )
    new_dataset.write(out_array.astype(out_array.dtype))
    new_dataset.close()

def cluster_pca(n_clusters, n_components, raster):
    raster  =np.rollaxis(raster,axis=1)
    raster  =np.rollaxis(raster,axis=2)
    raster  =np.rollaxis(raster,axis=1)
    row, col,band = raster.shape


    flat_raster = np.reshape(raster, (row*col,band))
    #flat_raster = np.ma.masked_where(flat_raster > 0, flat_raster)
    print("PCA_started")
    pca = PCA(n_components = n_components)
    print("PCA DONE")
    flat_raster = pca.fit_transform(flat_raster, 0)
    print("KMEANS started")
    kmeans = KMeans(n_clusters = n_clusters, init = 'k-means++').fit(flat_raster)
    print("KMEANS done")
	#center_means = kmeans.cluster_centers_
    labels = kmeans.labels_
    labels = np.reshape(labels, (row, col))
    return labels

def extract_VH_means(labels, raster, n_clusters):
    ndvi_mean =[]
    columns = []
    raster  =np.rollaxis(raster,axis=1)
    raster  =np.rollaxis(raster,axis=2)
    raster  =np.rollaxis(raster,axis=1)
    row, col, band = raster.shape
    raster = raster.astype('int64')
    flat_raster = np.reshape(raster, (row*col, band))
    flat_labels = np.reshape(labels, (row*col))
    for i in range(n_clusters):
        print(i)
        mean = np.mean(flat_raster[(flat_labels == i), :],axis=0)
        #mean = np.percentile(flat_raster[(flat_labels == i), :],95,axis=0)
        ndvi_mean.append(mean)
        columns.append('Mean_{}'.format(i))
        #np.save(str(i)+'_center_VH_mean.npy', mean)

    return ndvi_mean,columns


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

def MnVC(original):
    resampled = []
    for i in range(0, len(original), 2):
      j = i+1
      if len(original)%2==0:
        length = len(original)
      else:
        length = len(original)-1
      if i<length:
        temp_max = min(original[i], original[j])
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
    prev = next1 = 0
    j = -1
    thresh = abs(0.09*s.mean(resampled))
    while j < len(resampled)-2:
      j = j+1
      if resampled[j] < (moving_average[j]-200): #checking if the current value of list is less than the threshold w.r.t moving average list
        prev = j-1
        next1 = j+1
        while resampled[prev] < thresh and prev>0: #checking if the previous value is less than the threshold
            prev = prev-1
        while resampled[next1] < thresh and next1<len(resampled)-1: #likewise checking if the next value is less than the threshold
            next1 = next1+1
        #calculating the straight line dropout
        slope = (resampled[next1]-resampled[prev])/(next1-prev)
        c = resampled[next1] - (slope*next1)
        resampled[j] = abs((slope*j) + c)
    return resampled




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


def SG_weight(arr):
    if  sum(arr) == 0:
        return arr
    else:
        interp_ts = pd.Series(arr)
        interp_ts = interp_ts.interpolate(method='linear', limit=14)
    ##    print(interp_ts)
        smooth_ts = interp_ts

        wnd = 11
        order = 4
        F = 1e8
        W = None
        it = 0
        smoother_ts = savgol_filter(smooth_ts, window_length=wnd, polyorder=order)
##            print(smoother_ts)
        diff = smoother_ts - interp_ts
##            print(diff)
        sign = diff > 0
##            print(sign)
        if W is None:
            W = 1 - np.abs(diff) / np.max(np.abs(diff)) * sign
        return W.to_numpy()


def SG_filter(SG_list):
  SG_smooth = []
  for i in range(len(SG_list)):
    x = SG_list[i]
    smooth = savgol_filter(x, 11, 4)
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


def Timeseries_SWIR_Expand(Original_timeseries, Original_MVC_timeseries):
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
            Expanded_timeseries[i] = Original_timeseries[i]
        elif Original_MVC_timeseries[count] == Original_timeseries[j]:
            Expanded_timeseries[j] = Original_timeseries[j]

        count += 1
    return Expanded_timeseries

def Create_gap(mvng_avg, time_series):
    j = -1
    while j < len(mvng_avg)-2:
      j = j+1
      if time_series[j] < (mvng_avg[j]-200):
        time_series[j] =0

    return time_series

def Create_percentage_gap(mvng_avg, time_series):
    percent_list = (mvng_avg - time_series)/mvng_avg*100
    time_series[percent_list > 40] = 0

    return time_series

def Apply_cloud_mask(NDVI_list, Cloud_list, mvng_avg):
    NDVI_list[Cloud_list > 3] = 0
    NDVI_list[NDVI_list < (mvng_avg - 200)] = 0

    return NDVI_list

def Apply_SWIR_cloud_mask(SWIR_list, Cloud_list):
    SWIR_list[Cloud_list == 0] = 0

    return SWIR_list

def Fourier_smooth(Pix_list, harmonic_component):
    numbands = len(Pix_list)
    CorrVal = np.zeros((numbands), np.float)
    PI = float(22.0 / 7.0)
##    print "PI = " + str(PI)
    p = harmonic_component
    realpart= np.zeros((p+1), np.float)
    imagpart= np.zeros((p+1), np.float)

    for pp in  range (1, p+1): # this is hormonics component i am taking 4 as per literature
##        print('DFT Harmonic = ', pp)
        realpart[pp] = 0.0
        imagpart[pp] = 0.0
        for n in range (0, numbands):
            data = float(Pix_list[n])
##            print data
            realpart[pp] = realpart[pp] + float(2.0 / float(numbands)) * data * math.cos(2.0 * PI * float(pp-1) * float(n + 1) / float(numbands))
            imagpart[pp] = imagpart[pp] + float(2.0 / float(numbands)) * data * math.sin(2.0 * PI * float(pp-1) * float(n + 1) / float(numbands))
##        print realpart[pp]
##        print imagpart[pp]
##        print "gap"

##    print realpart[0]/2.0
    for n in range(0, numbands):
        outputsmoothedvalue = realpart[1] / 2.0

        for pp in range(2, p+1):
            outputsmoothedvalue = outputsmoothedvalue + (realpart[pp] * \
            math.cos((2.0 * PI * float(pp-1) * float(n + 1)) / float(numbands)))\
             + (imagpart[pp] * math.sin((2.0*PI * float(pp-1) * float(n + 1)) / float(numbands)))
##            print outputsmoothedvalue
##            print "p = " + str(pp) + " outval = " + str(outputsmoothedvalue)
        CorrVal[n] = outputsmoothedvalue
##        print "Gap"#CorrVal[n]

    return CorrVal

def replace_value (original_list, corrected_list):
    j = -1
    while j < len(original_list)-2:
      j = j+1
      if corrected_list[j] > (original_list[j]):
        corrected_list[j] = original_list[j]

    return corrected_list


def process_SWIR(df, cloud_arr):
    NDVI_list = (df.values).astype(float)
    cloud_list = (cloud_arr.values).astype(float)
##    moving_average = moving_avg(NDVI_list)

    MnVC_arr = MnVC(NDVI_list)
    Expanded_timeseries = Timeseries_SWIR_Expand(NDVI_list, MnVC_arr)
    Expanded_timeseries_gapfil = fill_gap(Expanded_timeseries)
    cloud_masked = Apply_SWIR_cloud_mask(Expanded_timeseries_gapfil, cloud_list)
    fill_gap_arr = fill_gap(cloud_masked)

    fill_gap_arr= replace_value(NDVI_list, fill_gap_arr)

    moving_average = moving_avg(fill_gap_arr)
    fill_gap_arr[fill_gap_arr > moving_average+50] = 0
    fill_gap_arr = fill_gap(fill_gap_arr)
    fill_gap_arr= replace_value(NDVI_list, fill_gap_arr)

    return fill_gap_arr

def main_process(df, cloud_arr):

    NDVI_list = (df.values).astype(float)
    cloud_list = (cloud_arr.values).astype(float)
##    final_list = []
    print(NDVI_list.dtype)
    print(len(NDVI_list))
    print(len(cloud_list))
    moving_average = moving_avg(NDVI_list)
    cloud_masked = Apply_cloud_mask(NDVI_list, cloud_list, moving_average)
##    MVC_pol = MVC(original_list)
    fill_gap_arr = fill_gap(cloud_masked)
    print(fill_gap_arr.shape)
    #print('MVC',len(MVC_pol))
    moving_average = moving_avg(np.array(fill_gap_arr))
    fill_gap_arr = fill_gap(Create_percentage_gap(moving_average, fill_gap_arr))
    MVC_pol = MVC(fill_gap_arr)
##    MVC_fill_gap_arr = fill_gap(np.array(MVC_dropout))
    #print('moving_average',len(moving_average))
##    MVC_dropout = straight_line_dropout_MA(MVC_pol, moving_average)
    #print('MVC_dropout',len(MVC_dropout))
##    fill_gap_arr = fill_gap(np.array(MVC_dropout))
##    SG_gap_arr = SG_Gapfill(np.array(fill_gap_arr))
    SG_gap_arr = savitzky_golay_filtering(np.array(MVC_pol)).to_list()
    Expanded_timeseries = Timeseries_Expand(fill_gap_arr, MVC_pol, SG_gap_arr)
    Expanded_timeseries_gapfil = fill_gap(Expanded_timeseries)
    fs_smooth = Fourier_smooth(Expanded_timeseries_gapfil, 18)


    return Expanded_timeseries_gapfil, fs_smooth



def cor_ndvi(labels, raster, n_clusters,final):
    raster  =np.rollaxis(raster,axis=1)
    raster  =np.rollaxis(raster,axis=2)
    raster  =np.rollaxis(raster,axis=1)
    row, col, band = raster.shape
    flat_raster = np.reshape(raster, (row*col, band))
    flat_labels = np.reshape(labels, (row*col))
    rascopy = flat_raster.copy()
    for i in range(n_clusters):
        rascopy[np.where(flat_labels == i)]=final[i]

    return rascopy


def extract_VH_means(labels, raster, n_clusters):
    ndvi_mean =[]
    columns = []
    raster  =np.rollaxis(raster,axis=1)
    raster  =np.rollaxis(raster,axis=2)
    raster  =np.rollaxis(raster,axis=1)
    row, col, band = raster.shape
    flat_raster = np.reshape(raster, (row*col, band))
    flat_labels = np.reshape(labels, (row*col))
    for i in range(n_clusters):
        #print(i)
        #mean = np.mean(flat_raster[(flat_labels == i), :],axis=0)
        mean = np.percentile(flat_raster[(flat_labels == i), :],85,axis=0)
        ndvi_mean.append(mean)
        columns.append('Mean_{}'.format(i))
        #np.save(str(i)+'_center_VH_mean.npy', mean)

    return ndvi_mean,columns

wnds=[11, 7]
orders=[2, 4]
def savitzky_golay_filtering(arr):
##    if  sum(arr) == 0 or arr[0] > 20000:
##        return arr
##    elif np.mean(arr, axis = 0) <= 2000:
##        return arr
    if  sum(arr) > 0:
        interp_ts = pd.Series(arr)
        interp_ts = interp_ts.interpolate(method='linear', limit=14)
    ##    print(interp_ts)
        smooth_ts = interp_ts
        wnd, order = 11, 4
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
        print(smooth_ts)
        return smooth_ts



# ===================== This block is for NDVI noise correction ========================================
farms_csv = pd.read_csv(r"F:\TN_6vill\new_csv\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_NDMI_med.csv")
farms_csv = farms_csv.reindex(sorted(farms_csv.columns), axis=1)
farms_csv = farms_csv.fillna(value=0)
fur_csv = farms_csv.copy()
NDVI_filter_col = [col for col in farms_csv if col.startswith(('VI','MI'))]
cloud_csv = pd.read_csv(r"F:\TN_6vill\new_csv\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_CLOUD_med.csv")
cloud_csv = cloud_csv.reindex(sorted(cloud_csv.columns), axis=1)
cloud_csv = cloud_csv.fillna(value=0)
CL_filter_col = [col for col in cloud_csv if col.startswith('CL')]
NDVI_len = len(farms_csv.index)
cloud_len = len(cloud_csv.index)





##if NDVI_len == cloud_len:
for i in range(NDVI_len):
    row_id = np.where(cloud_csv['field_uuid'] == farms_csv['field_uuid'][i])[0][0]
    print("row id", row_id)
    ndvi_col = [col for col in farms_csv if col.startswith(('VI','MI'))]
    NDVI_list = (farms_csv.iloc[i][ndvi_col])
    cloud_col = [col for col in cloud_csv if col.startswith('CL')]
    cloud_list = (cloud_csv.iloc[row_id][cloud_col])
    print(len(NDVI_list))
    print(len(cloud_list))
    if sum(NDVI_list.to_list()) > 0:
        noise_cor, Smooth = main_process(NDVI_list, cloud_list)
        cloud_list[cloud_list > 0] = 0
        cloud_list[NDVI_list.to_list() < (noise_cor-200)] = 1

        print(len(noise_cor))
        print(len(NDVI_filter_col))
        farms_csv.loc[i, NDVI_filter_col] = noise_cor
        fur_csv.loc[i, NDVI_filter_col] = Smooth
        cloud_csv.loc[i, CL_filter_col] = cloud_list
##        print(farms_csv.loc[i][2:])

farms_csv.to_csv(r'F:\TN_6vill\cor_data\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_NDMI_med_noise_cor.csv')
##fur_csv.to_csv(r'F:\TN_6vill\cor_data\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_NDVI_med_noise_cor_Fourier_smooth-H18.csv')
##cloud_csv.to_csv(r'F:\TN_6vill\cor_data\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_new_cloud_flag.csv')
##
###================================================End NDVI correction======================================================================
##
##
##
##
###=============================This block is for SWIR noise correction ======================================================================
##farms_csv = pd.read_csv(r'F:\TN_6vill\new_csv\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_SWIR_med.csv')
##farms_csv = farms_csv.reindex(sorted(farms_csv.columns), axis=1)
##farms_csv = farms_csv.fillna(value=0)
##SWIR_filter_col = [col for col in farms_csv if col.startswith('B11')]
##cloud_csv = pd.read_csv(r'F:\TN_6vill\cor_data\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_new_cloud_flag.csv')
##cloud_csv = cloud_csv.reindex(sorted(cloud_csv.columns), axis=1)
##cloud_csv = cloud_csv.fillna(value=0)
##CL_filter_col = [col for col in cloud_csv if col.startswith('CL')]
##SWIR_len = len(farms_csv.index)
##cloud_len = len(cloud_csv.index)
##
##for i in range(NDVI_len):
##    row_id = np.where(cloud_csv['field_uuid'] == farms_csv['field_uuid'][i])[0][0]
##    print("row id", row_id)
##    SWIR_list = (farms_csv.iloc[i][:-2])
##    cloud_list = (cloud_csv.iloc[row_id][:-3])
##    print(cloud_list)
##    print(len(SWIR_list))
##    print(len(cloud_list))
##    if sum(SWIR_list.to_list()) > 0:
##        new = main_process(NDVI_list, cloud_list)
##        new = process_SWIR(SWIR_list, cloud_list)
##        cloud_list[cloud_list > 0] = 0
##        cloud_list[NDVI_list.to_list() < (new-200)] = 1
##
##        print(len(new))
##        print(len(SWIR_filter_col))
##        farms_csv.loc[i, SWIR_filter_col] = new
##        cloud_csv.loc[i, CL_filter_col] = cloud_list
##
##farms_csv.to_csv(r'F:\TN_6vill\cor_data\Kollonkoil_model_part1_2_3_Merge_Updated_Apr14_SWIR_med_expand_mvng_avg_noise_cor.csv')
##
###==================================================================================================================================================








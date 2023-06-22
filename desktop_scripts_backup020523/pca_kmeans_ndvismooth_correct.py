#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 21:36:31 2022

@author: santhosh
"""

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

window_size = 3

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

'''
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
'''

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



def main_process(df):
    original_list = df.values
    final_list = []
    for i in range(len(original_list)):
        print(len(original_list[i]))
        #MVC_pol = MVC(original_list[i])
        #print('MVC',len(MVC_pol))
        #moving_average = moving_avg(MVC_pol)
        #print('moving_average',len(moving_average))
        #MVC_dropout = straight_line_dropout_MA(MVC_pol, moving_average)
        #print('MVC_dropout',len(MVC_dropout))
        #fill_gap_arr = fill_gap(np.array(MVC_dropout))
        #SG_gap_arr = SG_Gapfill(np.array(fill_gap_arr))
        smooth = savitzky_golay_filtering(original_list[i])
        #print('smooth',len(smooth))
        #Expanded_timeseries = Timeseries_Expand(original_list[i], MVC_pol, SG_gap_arr)
        #print('Expanded_timeseries',len(Expanded_timeseries))
        #Expanded_timeseries_gapfil = fill_gap(Expanded_timeseries)
        final_list.append(smooth)
    return final_list



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
    if  sum(arr) == 0 or arr[0] > 20000:
        return arr
    elif np.mean(arr, axis = 0) <= 2000:
        return arr
    else:
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
        return smooth_ts

kmeans_path = "H:/2021_22_WET_DRY_INDIVIDUAL_NDVI_MASK/PCA/KMEANS/"

for file in glob.glob('C:/Users/VassarGIS/Downloads/drive-download-20230323T100100Z-001/*.tif'):
    #file = r"H:/2021_22_WET_DRY_INDIVIDUAL_NDVI_MASK/annapurna_2021_2022_year_ndvi_mask_dry.img"
    print(file)
    outfile = os.path.dirname(file)+'/NDVI_cor/'+os.path.basename(file)[:-4]+'_cor_85.tif'
    #kmeans_raster = kmeans_path + os.path.basename(file)[:-4] + "_pca_kmeans.img"
    if not os.path.exists(outfile):
        print(file)
        ras = file
        ds= rio.open(ras).read()
        cluster = 200
        print("PCA and KMEANS started for: ",os.path.basename(file))
        labels = cluster_pca(n_clusters = cluster, n_components = 5, raster =ds)
        #labels = rio.open(kmeans_raster).read(1)
        cluster = np.max(labels)
        print(cluster)
        print(labels.shape)
        #np.save(file[:-4]+'_labels.npy', labels)
        print("Computing 85th percentile at each cluster: ",os.path.basename(file))
        ndvi,column = extract_VH_means(labels, ds, cluster)
        ab = np.array(ndvi)
        df = pd.DataFrame(ab)
        print("SG filter ongoing")
        final_18_19 = main_process(df)
        print("SG filter done")
        print("Replacing original image with smoothened NDVI")
        final_arr = cor_ndvi(labels, ds, cluster,final_18_19)
        print("Replaced original image with smoothened NDVI")
        final_arr = np.rollaxis(final_arr,axis=1)
        final_arr = final_arr.reshape(ds.shape)
        if os.path.isdir(os.path.dirname(file)+'/NDVI_cor/') is False:
            os.mkdir(os.path.dirname(file)+'/NDVI_cor/')
        raster_writer(ras, final_arr, outfile)



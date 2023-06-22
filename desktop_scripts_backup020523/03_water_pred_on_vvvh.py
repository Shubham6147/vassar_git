import os
import sys
import shutil
import glob

import rasterio
import joblib
import numpy as np

from rasterio.windows import Window
import time



def water_pred_sen1(raster_path, pred_output_path):

    """
    Runnning Random forest prediction model for water prediction on sentinel 1 vv+vh data.


    Args:
    	raster_path (string): input raster sen1 vvvh stacked geotiff (output of snap preprocessing step)
    	pred_output_path (string): prediction raster containg water - 1,  non-water - 0, no-data - 4

    """

    model_path = r"E:\tg_mitank\scripts\RGB_Bin_RFM_ET_34.joblib"
    model = joblib.load(model_path)
    model.n_jobs = -1
    src = rasterio.open(raster_path)
    meta_data = src.meta
    wd = src.width
    ht = src.height
    widths = list(np.arange(0, wd, 5000))
    heights = list(np.arange(0, ht, 5000))
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
    	count=1,
    	dtype=np.ubyte,
    	crs=meta_data['crs'],
    	compress='DEFLATE',
    	transform=meta_data['transform'],
    	BIGTIFF='YES'
    )

    for w in range(len(widths)-1):
    	for h in range(len(heights)-1):

    		data = src.read(window=Window.from_slices((heights[h], heights[h+1]), (widths[w], widths[w+1])))/100

    		out_data = np.power(10, data/10)

    		vh_data = out_data[1,:,:]
    		vv_data = out_data[0,:,:]

    		#Coeficients
    		c1 = 0.001
    		c2 = 0.01
    		c3 = 0.02
    		c4 = 0.03
    		c5 = 0.045
    		c6 = 0.05
    		c7 = 0.9
    		c8 = 0.25

    		#Red Band
    		temp_vv_data = vv_data.copy()
    		temp_vv_data[temp_vv_data < 0.001] = 0.001
    		red_band = c4 + np.log ((c1 - np.log (c6 / (c3 + 50 * temp_vv_data))))
    		red_band[temp_vv_data == 1] = 0
    		red_band = red_band.reshape((1,data.shape[1],data.shape[2]))

    		#Green Band
    		green_band = c6 + np.exp (c8 * (np.log (c2 + 2 * vv_data) + np.log (c3 + 5 * vh_data)))
    		green_band[vv_data == 1] = 0
    		green_band = green_band.reshape((1,data.shape[1],data.shape[2]))

    		#Blue Band
    		blue_band = 0.5 + np.log((c8 / (c5 + 5 * vv_data)))
    		blue_band[vv_data == 1] = 0
    		blue_band = blue_band.reshape((1,data.shape[1],data.shape[2]))

    		rgb_data  = np.concatenate((red_band, green_band, blue_band), axis = 0)

    		new_data = np.empty(rgb_data.shape)

    		ref_min_values = [-1.0562721, 0, -10.9945755]
    		ref_max_values = [2.7648606, 38.288673, 2.2143126]

    		for i in range(rgb_data.shape[0]):
    			band_data = rgb_data[i,:,:]
    			band_data[band_data < ref_min_values[i]] = ref_min_values[i]
    			band_data[band_data > ref_max_values[i]] = ref_max_values[i]

    			new_data[i,:,:] = ((band_data - ref_min_values[i])/(ref_max_values[i] - ref_min_values[i]))*255 + 1
    		indexes = np.argwhere(np.all((rgb_data == 0), axis = 0))

    		new_data[:,indexes[:,0],indexes[:,1]] = 0
    		new_data = np.round(new_data, decimals = 0)
    		new_data[new_data >= 255] = 255
    		new_data[new_data <= 0] = 0

    		#RGB array
    		rgb_arr = new_data[:,:,:].reshape((3,new_data.shape[1],new_data.shape[2])).astype(np.ubyte)


    		data = np.rollaxis(rgb_arr,0,3)
    		flatten_data = data.reshape((data.shape[0]*data.shape[1], data.shape[2]))
    		X_data = flatten_data[:,:]
    		print(X_data)

    		pred_arr = model.predict(X_data)
    		pred_arr[~np.all(X_data, axis = 1)] = 4
    		pred_arr = pred_arr.reshape((data.shape[0],data.shape[1],1))
    		pred_arr = np.rollaxis(pred_arr,2,0)




    		pred_dataset.write(pred_arr.astype(np.ubyte), window=Window.from_slices((heights[h], heights[h+1]), (widths[w], widths[w+1])))

    pred_dataset.close()
    src.close()

import glob

files = glob.glob('F:/KTCC/sen1/*.tif')
output_path = 'F:/KTCC/pred/'
for filen in files:
    filename = os.path.basename(filen)
    pred_output_path = output_path + 'pred_' + filename
    water_pred_sen1(filen, pred_output_path)
##def main():
##	#args = sys.argv[1].split(",")
##	input_path = sys.argv[1]
##	pred_output_path = sys.argv[2]
##
##	water_pred_sen1(input_path, pred_output_path)
##
##if __name__ == '__main__':
##	main()

import os 
import sys
from shapely.geometry.polygon import Polygon
import geopandas as gpd
from osgeo import gdal
import numpy as np

import rasterio 

from skimage import measure
from shapely import speedups

import itertools

speedups.disable()

def clipping(raster, waterbodies, clipped_path):
    """
    Function for identifying the mi-tanks which are overlapping with the raster.

    Args:
        raster (string): path to the water prediction raster.
        waterbodies (_type_): Entire Mi-Tanks shapefile
        clipped_path (_type_): Output file path of clipped Mi-Tanks 

    Returns:
        string : Output file path of clipped Mi-Tanks
    
    """
    File = gdal.Open(raster)
    width = File.RasterXSize
    height = File.RasterYSize
    gt = File.GetGeoTransform()
    minx = gt[0]
    miny = gt[3] + width*gt[4] + height*gt[5]
    maxx = gt[0] + width*gt[1] + height*gt[2]
    maxy = gt[3]
    bbox = Polygon([(minx, miny),(minx, maxy),(maxx, maxy),(maxx, miny)])

    shp = gpd.read_file(waterbodies)
    shp['centroid'] = shp['geometry'].centroid
    shp['intersect'] = shp['centroid'].intersects(bbox)
    shp2 = shp[shp['intersect'] == True]

    shp2 = shp2.drop(['centroid','intersect'], 1)
    if shp2.shape[0] == 0:
        return 'Empty'
    shp2.to_file(clipped_path)
    return (clipped_path)


#------------------ function for changining raster resolution and extend  -------------------------------------
def get_extent(filename):
	raster =  rasterio.open(filename)
	geoTransform = raster.meta['transform']
	minx = geoTransform[2]
	maxy = geoTransform[5]
	maxx = minx + geoTransform[0] * raster.meta['width']
	miny = maxy + geoTransform[4] * raster.meta['height']
	return [minx, miny, maxx, maxy]


def ChangeResolutionAndExtend(reference_path, input_path, output_path):
    raster =  rasterio.open(reference_path)
    geoTransform = raster.meta['transform']
    minx = geoTransform[2]
    maxy = geoTransform[5]
    maxx = minx + geoTransform[0] * raster.meta['width']
    miny = maxy + geoTransform[4] * raster.meta['height']

    PixelValue = geoTransform[0]

    command = 'gdalwarp -r near -multi -wo "NUM_THREADS=ALL_CPUS" -tr ' + \
    			str(PixelValue) + " " + str(PixelValue) + " -te " + str(minx) + " " + str(miny) + " " + str(maxx) + " " + str(maxy) + " " \
				+ input_path + " " + output_path
    
    #print(command)
    os.system(command)


def intersect(poly_bbox, tile_bbox):
	box1 = Polygon([[poly_bbox[0],poly_bbox[3]], [poly_bbox[2],poly_bbox[3]], [poly_bbox[2],poly_bbox[1]], [poly_bbox[0],poly_bbox[1]]])
	box2 = Polygon([[tile_bbox[0],tile_bbox[3]], [tile_bbox[2],tile_bbox[3]], [tile_bbox[2],tile_bbox[1]], [tile_bbox[0],tile_bbox[1]]])

	intersect_area = box1.intersection(box2).area
	if intersect_area > 0:
		#print('Intersect area:', intersect_area)
		return True
	else:
		return False



#====================1

def remove_pixels(input_mask, thre):
	labels_mask = measure.label(input_mask)
	regions = measure.regionprops(labels_mask)

	region_area = []
	for i in range(len(regions)):
		region_area.append(regions[i].area)

	if len(regions) > 1:
		for i in range(len(regions)):
			rg = regions[i]
			area = region_area[i]
			if area <= thre:
				labels_mask[rg.coords[:,0], rg.coords[:,1]] = 0
	labels_mask[labels_mask!=0] = 1
	mask = labels_mask
	return(mask)

def replace_nodata(raster):
	new_raster = raster.copy()
	bands, xmax, ymax = raster.shape
	indexes = np.argwhere(raster == 4)
	for index in indexes:
		x_index, y_index = index[1:]
		x_indexs = np.array([x_index, x_index+1, x_index+2, x_index-1, x_index-2])
		y_indexs = np.array([y_index, y_index+1, y_index+2, y_index-1, y_index-2])
		x_indexs[x_indexs > xmax-1] = xmax-1
		x_indexs[x_indexs < 0] = 0
		y_indexs[y_indexs > ymax-1] = ymax-1
		y_indexs[y_indexs < 0] = 0
		kernel_indexes = np.array(list(itertools.product(x_indexs, y_indexs)))
		#print(raster[:, kernel_indexes[:,0], kernel_indexes[:,1]])
		lst = raster[:, kernel_indexes[:,0], kernel_indexes[:,1]].tolist()[0]
		new_raster[0, x_index, y_index] = max(set(lst), key=lst.count)
	return new_raster


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
		dtype=meta_data['dtype'],
		crs=meta_data['crs'],
		transform=meta_data['transform'],
	)
	new_dataset.write(data.astype(meta_data['dtype']))
	new_dataset.close()





import rasterio
#import shapefile
import geopandas as gpd
import numpy as np
#from osgeo import gdal
import os
import matplotlib.pyplot as plt
#from get_mitank import clipping
import fiona
from postgres import *
from bulk_processing_constants import *
import pandas as pd
from rasterio.mask import mask

def Get_max_area(DEM_path, pixel_unit, conversion_unit):
	dem_data = rasterio.open(DEM_path).read()
	dem_data[dem_data>0] = 1
	dem_data[dem_data<0] = 0
	pix_count = np.sum(dem_data)
	pix_area = (pixel_unit*pixel_unit)*conversion_unit
	WSA_area = pix_count * pix_area
	return float(WSA_area)

def Get_max_Volume(DEM_path, pixel_unit, conversion_unit):
	dem_data = rasterio.open(DEM_path).read()
	dem_data[dem_data == np.nan] = 0
	dem_data[dem_data <= 0] = 0
	elev_max = np.percentile(dem_data, 99.25)
	WSA_depth = elev_max-dem_data
	WSA_depth[dem_data <= 0] = 0
	WSA_depth[WSA_depth <= 0] = 0
	pix_area = (pixel_unit*pixel_unit)*conversion_unit
	#print(pix_area)
	#print("DEPTH ",np.sum(WSA_depth))
	#print("DEPTH max ",np.max(WSA_depth))
	vol = (WSA_depth * pix_area * 35.5)
	return float(np.sum(vol))

def get_dem(esa_dem_path, mitanks_shp_path, output_dir, polygon_id, pixel_unit, conversion_unit):
	print('ESA DEM', esa_dem_path)
    gdf = gpd.read_file(mitanks_shp_path)
	shapefile = fiona.open(mitanks_shp_path)
	esa_dem = rasterio.open(esa_dem_path)
	insert_list = ()
	df = pd.DataFrame()
	id1 =[]
	area =[]
	vol =[]
	for i in range(len(shapefile)):
		name = str(shapefile[i]['properties'][polygon_id])
		print('Tank id',name)
		shape = shapefile[i]['geometry']

		out_image, out_transform = mask(esa_dem, [shape], crop=True, all_touched = True)
		out_meta = esa_dem.meta

		out_meta.update({"driver": "GTiff",
			"height": out_image.shape[1],
			"width": out_image.shape[2],
			"compress": "DEFLATE",
			"transform": out_transform})

		with rasterio.open(output_dir+str(name)+".tif", "w", **out_meta) as dest:
			dest.write(out_image)
			dest.close()

		#id1.append(name)
		#area.append(Get_max_area(output_dir+name+".tif", pixel_unit, conversion_unit))
		vol.append(Get_max_Volume(output_dir+name+".tif", pixel_unit, conversion_unit))

	#df['id'] = id1
	#df['max_area'] = area
	gdf['capacity'] = vol

	return gdf
		#value = [name, shapefile[i]['properties']['vill_name'], shapefile[i]['properties']['mandal'], shapefile[i]['properties']['tank_name'], Get_max_Volume(output_dir+name+".tif", pixel_unit, conversion_unit), Get_max_area(output_dir+name+".tif", pixel_unit, conversion_unit)]
		#insert_list = insert_list + (value,)

	#insert_in_mitank_maxvol_table(insert_list,maxvol_dbname,maxvol_user,maxvol_password,maxvol_host)

#get_dem('/home/santhosh/Downloads/ktcc_alos_esa_dem_merge_edit_float_new_10m_resample2_filter_clip.tif', '/home/santhosh/Music/mitank/TNWRIS/KTCC_MI_tank_metadata_updated_final_275.shp', '/home/santhosh/Music/mitank/TNWRIS/TN_MITank_DEM/', 'geoid', 9.9, 0.000001)
gdf = get_dem(r"E:\DEM\ALOS\odisha_final_10m_snap.tif", r'C:/Users/VassarGIS/Downloads/recorrectodishamitankboundaries/odisha_waterbody_uuid.shp' , r'C:/Users/VassarGIS/Downloads/drive-download-20230102T053005Z-001/clip_dem_2/', "tank_geoid", 9.9, 0.000001)

gdf.to_file(r'C:/Users/VassarGIS/Downloads/recorrectodishamitankboundaries/odisha_waterbody_uuid.shp')
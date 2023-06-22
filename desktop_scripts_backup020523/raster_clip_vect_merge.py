
import shapefile
import os, sys, glob
from wsa_functions import clipping
import rasterio
from rasterio.mask import mask
import fiona
from rasterstats import zonal_stats
from shapely.geometry import shape, mapping
from shapely.geometry import Polygon
import shapefile
import fiona
from scipy.ndimage import gaussian_filter1d
import numpy as np
from shapely.geometry.multipolygon import MultiPolygon
import os, sys
import rasterio

import geopandas as gpd
from osgeo import ogr
from shapely.wkt import loads


def clipMitanks(shp_file, raster, cloud, output_dir, polygonId):
	"""_summary_

	Args:
		shp_file (_type_): _description_
		raster (_type_): _description_
		cloud (_type_): _description_
		output_dir (_type_): _description_
		polygonId (_type_): _description_

	Returns:
		_type_: _description_
	"""


	print(raster)
	output_clipped_mi_tanks = 	output_dir+"mi_tank_clipped.shp"
	state = clipping(raster, shp_file, output_clipped_mi_tanks)
	if state == 'Empty':
		return False
	r = shapefile.Reader(output_clipped_mi_tanks)

	total_shapes = len(r.records())
	print("totalshapes",total_shapes)
	if total_shapes!= 0  and os.path.exists(output_clipped_mi_tanks):

		stats = zonal_stats(output_clipped_mi_tanks, raster, categorical = True, geojson_out = True, nodata = -1, stats='count')
		wsa_mitanks_dic = {}
		for stat in stats:
			wsa_mitanks_dic[stat['properties'][polygonId]] = stat['properties']
		if cloud != 'null':
			stats = zonal_stats(output_clipped_mi_tanks, cloud, categorical = True, geojson_out = True, nodata = -1, stats='count')
			cloud_mitanks_dic = {}
			for stat in stats:
				cloud_mitanks_dic[stat['properties'][polygonId]] = stat['properties']

		shp_data = fiona.open(output_clipped_mi_tanks)
		raster_data = rasterio.open(raster)
		for i in range(total_shapes):
			print(i)
			name = str(shp_data[i]['properties'][polygonId])
			shape = shp_data[i]['geometry']
			print(name)
			out_image, out_transform = mask(raster_data, [shape], crop=True, nodata=0, all_touched = True)
			out_meta = raster_data.meta

			out_meta.update({"driver": "GTiff",
				"height": out_image.shape[1],
				"width": out_image.shape[2],
				"compress": "DEFLATE",
				"transform": out_transform})

			with rasterio.open(output_dir+str(name)+"_temp.tif", "w", **out_meta) as dest:
				dest.write(out_image)
				dest.close()

			#if 4 in wsa_mitanks_dic[name].keys() and (wsa_mitanks_dic[name][4]/wsa_mitanks_dic[name]['count'])*100 >= 20:
				#os.system('rm '+output_dir+name+"_temp.tif")

			#elif cloud != 'null':
				#if 1 in cloud_mitanks_dic[name].keys() or 2 in cloud_mitanks_dic[name].keys():
					#os.system('rm '+output_dir+name+"_temp.tif")

			#modify waterpred and remove this-----not required if the input is in 4326 and compression is deflate
			if os.path.exists(output_dir+str(name)+"_temp.tif"):
				cmd = "gdalwarp -t_srs EPSG:4326 -ot Byte -co compress=DEFLATE "+ output_dir+name+"_temp.tif " + output_dir+name+".tif"
				os.system(cmd)
				os.remove(output_dir+name+"_temp.tif")
			#-------------------------------------------

	os.system('rm -r '+output_dir+"mi_tank_clipped*")


def segmentize(geom):
    wkt = geom.wkt  # shapely Polygon to wkt
    geom = ogr.CreateGeometryFromWkt(wkt)  # create ogr geometry
    geom.Segmentize(0.0003)  # densify geometry with the given distance in map units
    wkt2 = geom.ExportToWkt()  # ogr geometry to wkt
    new = loads(wkt2)  # wkt to shapely Polygon
    return new


def Vectorize(raster_path, output_dir, mitank_id):
    """_summary_

    Args:
    	raster_path (_type_): _description_
    	output_dir (_type_): _description_
    	mitank_id (_type_): _description_
    	date (_type_): _description_
    	source (_type_): _description_
    	projection (_type_): _description_
    	sigma (_type_): _description_

    output:


    """
    #gdal command to polygonise the raster
    command = "gdal_polygonize.py "+ raster_path + " " + output_dir + "temp_" + mitank_id+".shp "
    print(command)
    os.system(command)

    #read geopandas and remove background pixcels
    gpd_shp = gpd.read_file(output_dir+"temp_"+mitank_id+".shp")
    gpd_shp = gpd_shp.loc[gpd_shp['DN'] != 0 ]

    #adding segments to the polygon to make shapefile more beautiful
    gpd_shp['geometry'] = gpd_shp['geometry'].map(segmentize)

    gpd_shp['mitank_id'] = str(mitank_id)
    #gpd_shp['date'] = str(date)
    #gpd_shp['source'] = str(source)
    #gpd_shp.rename(columns={'DN': 'depth'})

    #saving the shapefile
    gpd_shp.to_file(output_dir+mitank_id+".shp")

    os.system("rm -r "+output_dir+"temp_"+mitank_id+"*")



#clipMitanks("F:/OD_new_MI_Tank/buffer/points_buffer.shp","F:/odisha_water_threshold_10.tif",'null', 'F:/OD_new_MI_Tank/clip/','OBJECTID')

for filee in os.listdir('F:/OD_new_MI_Tank/clip/'):
            Vectorize('F:/OD_new_MI_Tank/clip/'+filee,'F:/OD_new_MI_Tank/vect/', filee[:-4])





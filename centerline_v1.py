import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import mapping, shape
from centerline.geometry import Centerline
import geopandas as gpd
import pandas as pd
import multiprocessing as  mp
from shapely import geometry, ops


def draw_centerline(polygon):
    try:
        centerline = Centerline(polygon, interpolation_distance=0.00001)
        clipped_gpd = gpd.GeoDataFrame(geometry=gpd.GeoSeries(centerline.geometry.geoms))
        shapely_multiline = geometry.MultiLineString(list(clipped_gpd.geometry))
        #clipped_gpd_2 = gpd.GeoDataFrame(geometry=results)
        return shapely_multiline
    except:
        #print('pass')
        pass

def divide_in_grid(aoi):

    #aoi = gpd.read_file(gfp)
    aoi = aoi.to_crs('EPSG:4326')

    polygons = []
    name = []


    xmin, ymin, xmax, ymax = aoi.total_bounds

    length = 0.001
    wide = 0.001

    cols = list(np.arange(xmin, xmax + wide, wide))
    rows = list(np.arange(ymin, ymax + length, length))


    for x in cols[:-1]:
        for y in rows[:-1]:
            polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))


    grid = gpd.GeoDataFrame({'geometry':polygons})
    grid = grid.set_crs(aoi.crs)
    intersection = aoi.overlay(grid, how='intersection')
    intersection.crs = "EPSG:4326"
    intersection = intersection.explode()

    return intersection


src = '/mnt/c/Users/shubh/Downloads/trial_farm_bound/dn_value_2_difference_2.shp'
dst = '/mnt/c/Users/shubh/Downloads/trial_farm_bound/dn_value_2_difference_2_cen.shp'


shp_file = gpd.read_file(src)
#split_polygon = divide_in_grid(shp_file)
polygon_list = list(shp_file.geometry)

print(len(polygon_list))


with mp.Pool() as p:
    results = p.map(draw_centerline, polygon_list)#, chunksize=10)


centerline = gpd.GeoDataFrame(geometry=results)
centerline.to_file(dst)


#intersection = divide_in_grid(gfp)

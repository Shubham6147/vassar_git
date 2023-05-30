import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import mapping, shape
from centerline.geometry import Centerline
import geopandas as gpd
import pandas as pd



def divide_in_grid(gfp):

    aoi = gpd.read_file(gfp)
    aoi = aoi.to_crs('EPSG:4326')

    polygons = []
    name = []


    xmin, ymin, xmax, ymax = aoi.geometry.bounds

    length = 0.01
    wide = 0.01

    cols = list(np.arange(xmin, xmax + wide, wide))
    rows = list(np.arange(ymin, ymax + length, length))


    for x in cols[:-1]:
        for y in rows[:-1]:
            polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))


    grid = gpd.GeoDataFrame({'geometry':polygons})
    grid.to_file("C:/Users/shubh/Downloads/MNCF_AGRI_DEMO/bound_5_dist_grid.shp")


    grid = grid.set_crs(aoi.crs)
    #grid.to_file(r"C:\Users\shubh\Downloads\MP_shivpuri_karera_tesil_poly_for_segmentation/mp_shivpuri_karera_tehsil_grid.shp")

    intersection = aoi.overlay(grid, how='intersection')

    intersection.crs = "EPSG:4326"

    #with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
        #intersection.to_file(r"D:/mncfc/mp_tehsil_2/mp_shivpuri_karera_tehsil_grid_4.shp")

    return intersection

def draw_centerline(polygon):

    centerline = Centerline(polygon, interpolation_distance=0.5)
    rows['geom_2'] = centerline.geometry.geoms
    clipped_gpd = gpd.GeoDataFrame(geometry=gpd.GeoSeries(centerline.geometry.geoms))

    return clipped_gpd







src = 'C:/Users/shubh/Downloads/ne_10/ne_10.shp'
dst = 'C:/Users/shubh/Downloads/ne_10/ne_10_CEN.shp'



shp_file = gpd.read_file(src)
shp_file = shp_file.to_crs("EPSG:3857")

shp_file['geom_2'] = ''




polygons = []

polygon_list = list(shp_file.geometry)

with mp.Pool() as p:
    results = p.map(draw_centerline, polygon_list, chunksize=100)





for index, rows in shp_file.iterrows():
    #print(index)

    polygon = shape(rows.geometry)
    try:

        with mp.Pool() as p:
            results = p.map(draw_centerline, id_geom_list, chunksize=100)

        centerline = Centerline(polygon, interpolation_distance=0.5)

        rows['geom_2'] = centerline.geometry.geoms
        #print('working')
        clipped_gpd = gpd.GeoDataFrame(geometry=gpd.GeoSeries(centerline.geometry.geoms))
        polygons.append(clipped_gpd)
        #break
    except:
        print('not working')


clipped_shp = gpd.GeoDataFrame(pd.concat(polygons))
clipped_shp.to_file(dst)


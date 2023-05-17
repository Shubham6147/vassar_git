from shapely.geometry import Polygon
from shapely.geometry import mapping, shape
from centerline.geometry import Centerline
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np
import pandas as pd




def divide_in_grid(gpf):

    points = gpd.read_file('C:/Users/shubh/Downloads/MNCF_AGRI_DEMO/bound_5_dist.shp')

    polygons = []
    name = []
    for index, row in points.iterrows():
        print(row.geometry.bounds)


        xmin, ymin, xmax, ymax = row.geometry.bounds

        length = 0.05
        wide = 0.05

        cols = list(np.arange(xmin, xmax + wide, wide))
        rows = list(np.arange(ymin, ymax + length, length))

        id_aoi = 1
        for x in cols[:-1]:
            for y in rows[:-1]:
                name_id = str(row.dtname) + '_' + str(id_aoi)
                name.append(name_id)
                polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))

                id_aoi = id_aoi + 1

    grid = gpd.GeoDataFrame({'name': name, 'geometry':polygons})
    grid.to_file("C:/Users/shubh/Downloads/MNCF_AGRI_DEMO/bound_5_dist_grid.shp")




src = 'C:/Users/shubh/Downloads/ne_10/ne_10.shp'
dst = 'C:/Users/shubh/Downloads/ne_10/ne_10_CEN.shp'


shp_file = gpd.read_file(src)

shp_file['geom_2'] = ''

all_rows = []
#shp_file = shp_file[1:]
for index, rows in shp_file.iterrows():
    print(index)

    polygon = shape(rows.geometry)
    try:
        centerline = Centerline(polygon)

        rows['geom_2'] = centerline.geometry.geoms
        print('working')

        all_rows.append(rows)

        #break
    except:
        print('not working')

centerline_out = pd.concat(all_rows)

centerline_out = gpd.GeoDataFrame(centerline_out, geometry='geom_2')

centerline_out = centerline_out.drop('geometry', axis= 1)


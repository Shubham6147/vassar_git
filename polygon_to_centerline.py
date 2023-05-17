from shapely.geometry import Polygon
from shapely.geometry import mapping, shape
from centerline.geometry import Centerline
import geopandas as gpd
from shapely.geometry import Polygon
import numpy as np



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



def divide_shapefie_in_grids(aoi):

    prefix_name = os.path.basename(aoi).split(".")[0]

    aoi = gpd.read_file(aoi_fp)

    if 'name' in list(aoi.columns):
        aoi = aoi.drop('name', axis = 1)

    aoi_3857 = aoi.to_crs("EPSG:3857")
    aoi['area'] = aoi_3857['geometry'].area

    print(aoi.crs)


    polygons = []
    name = []


    for index, row in aoi.iterrows():



        if row.area > 10000000:

            #print(row.geometry.bounds)


            xmin, ymin, xmax, ymax = row.geometry.bounds

            length = 0.05
            wide = 0.05

            cols = list(np.arange(xmin, xmax + wide, wide))
            rows = list(np.arange(ymin, ymax + length, length))

            id_aoi = 1
            for x in cols[:-1]:
                for y in rows[:-1]:
                    name_id = str(prefix_name) + '_' + str(id_aoi)
                    name.append(name_id)
                    polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))

                    id_aoi = id_aoi + 1

        else:
            polygons.append(row.geometry)

    grid = gpd.GeoDataFrame({'name': name, 'geometry':polygons})
    grid = grid.set_crs(aoi.crs)
    #grid.to_file(r"C:\Users\shubh\Downloads\MP_shivpuri_karera_tesil_poly_for_segmentation/mp_shivpuri_karera_tehsil_grid.shp")

    intersection = aoi.overlay(grid, how='intersection')

    intersection.crs = "EPSG:4326"

    with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
        intersection.to_file(r"D:/mncfc/mp_tehsil_2/mp_shivpuri_karera_tehsil_grid_4.shp")

    return intersection






src = 'C:/Users/shubh/Downloads/dn1/kmg_dn1_clip_4326.shp'
dst = 'C:/Users/shubh/Downloads/dn1/kmg_dn1_clip_cen.shp'


shp_file = gpd.read_file(src)

shp_file['geom_2'] = ''
#shp_file = shp_file[1:]
for index, rows in shp_file.iterrows():
    print(index)

    polygon = shape(rows.geometry)
    try:
        centerline = Centerline(polygon)

        rows['geom_2'] = centerline.geometry.geoms
        print('working')
        break
    except:
        print('not working')

import geopandas as gpd
from shapely.geometry import Polygon
from samgeo import tms_to_geotiff, get_basemaps
import numpy as np
import fiona
import gdal




aoi_fp = r"C:\Users\shubh\Downloads\MP_shivpuri_karera_tesil_poly_for_segmentation\mp_shivpuri_karera_tehsil.shp"
out_path = out_path = 'D:/mncfc/mp_tehsil_2'

def divide_shapefie_in_grids(aoi):

    prefix_name = os.path.basename(aoi).split(".")[0]

    aoi = gpd.read_file(aoi_fp)
    aoi_3857 = aoi.to_crs("EPSG:3857")
    aoi['area'] = aoi_3857['geometry'].area


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

    #with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
        #intersection.to_file(r"C:\Users\shubh\Downloads\MP_shivpuri_karera_tesil_poly_for_segmentation/mp_shivpuri_karera_tehsil_grid_4.shp")

    return intersection



def download_basemap(aoi, out_path,  google= True):

    intersection = divide_shapefie_in_grids(aoi)

    for index , row in intersection.iterrows():
        boundbox  = list(row.geometry.bounds)



        filename = str(row['name']) + '.tif'
        tms2geotiff_output = os.path.join(out_path, filename)

        if google:
            # Google Imagery
            tms_to_geotiff(output=output_image, bbox=boundbox, resolution = 0.5, source='Satellite')
        else:
            #Bing Imagery
            tms_to_geotiff(output=output_image, bbox=boundbox, resolution=0.5, source='Esri.WorldImagery')


        final_filepath = tms2geotiff_output[:-4] + '_0.5m.jp2'

        xres = 0.5
        yres = 0.5
        resample_alg = 'near'

        ds = gdal.Warp(final_filepath, tms2geotiff_output, warpoptions=dict(xRes=xres, yRes=yres, resampleAlg=resample_alg))

        ds = None



download_basemap(aoi, out_path,  google= True)









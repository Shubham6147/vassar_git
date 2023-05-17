import geopandas as gpd
from shapely.geometry import Polygon, mapping
import glob

shp_files = glob.glob('C:/Users/shubh/Downloads/shps_for_segmentation/shps/*.shp')



def linestring_to_polygon(fili_shps):
    #gdf = gpd.read_file(fili_shps) #LINESTRING
    fili_shps['geometry'] = [Polygon(mapping(x)['coordinates']) for x in fili_shps.linestring]
    return gdf

for shp_file in shp_files:
    gdf = gpd.read_file(shp_file)
    gdf['dissolve'] = 1
    dissloved = gdf.dissolve('dissolve')

    dissloved['linestring'] = dissloved.exterior
    linestring_to_polygon(gdf)

    break

import gdal
import geopandas as gpd

grid = gpd.read_file('D:/aus_v2/iwm_0.05_aus_uuid_all.shp')
aoi = gpd.read_file('D:/aus_v2/aus_states.shp')


intersection = aoi.overlay(grid, how='intersection')

intersection.crs = "EPSG:4326"

with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
    intersection.to_file(r"D:/aus_v2/aus_states_intersection.shp")



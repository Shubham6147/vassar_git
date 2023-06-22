import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point

gdf = gpd.read_file('')

gdf["geometry2"] = gdf.representative_point()

gdf = gdf.set_geometry('geometry2')

gdf.to_file('')
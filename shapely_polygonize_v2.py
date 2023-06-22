import geopandas
from shapely.ops import polygonize

gdf = geopandas.read_file(r"C:\Users\shubh\Downloads\682524c2-3837-4c7c-b325-f1e26ddf3bcaaoi_extendline\682524c2-3837-4c7c-b325-f1e26ddf3bcaaoi_extendline.shp")

gdf = gdf.dissolve()
polygons = geopandas.GeoSeries(polygonize(gdf.geometry))
polygons = polygons.set_crs('epsg:3857')

#polygons.plot()

polygons.to_file(r'C:\Users\shubh\Downloads\poly\poly_5.gpkg')

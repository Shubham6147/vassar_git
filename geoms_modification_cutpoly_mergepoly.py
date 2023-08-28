import geopandas as gpd
from shapely.ops import linemerge, unary_union, polygonize
from shapely.geometry import LineString, Polygon

# Define the Polygon and the cutting line
line = gpd.read_file('C:/Users/shubh/Downloads/geom_modi/cutline.shp')
input_polygon = gpd.read_file('C:/Users/shubh/Downloads/geom_modi/merge.shp')

polygon = input_polygon[input_polygon['fid'] == 837].geometry.values[0]

cut_line = line.geometry.values[0]
polys = input_polygon.geometry. values

def cut_polygon_by_line(input_polygon, cut_line):
    merged = linemerge([polygon.boundary, cut_line])
    borders = unary_union(merged)
    polygons = polygonize(borders)
    return list(polygons)

#returns shapely polygons
polygons_cut = cut_polygon_by_line(input_polygon, cut_line)

#returns shapely polygon
mergedPolys = unary_union(polys)

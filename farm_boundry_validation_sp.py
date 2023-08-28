import uuid
import pandas as pd
from pyproj import CRS
import geopandas as gpd
from shapely.geometry import MultiPolygon, Polygon
from sqlalchemy import create_engine



def fix_invalid_geometries(gdf):
    '''
    gdf: Input will be in epsg:4326 projection

    '''
    # Create a copy of the GeoDataFrame to avoid modifying the original data
    gdf_copy = gdf.copy()

    # Apply the buffer(0) operation to fix invalid geometries
    gdf_copy.geometry = gdf_copy.geometry.buffer(0)

    #Get the count of farms after fix-geometry
    count_after_fix_geometry = len(gdf_copy)

    return gdf_copy, count_after_fix_geometry


def calculate_area_in_utm(input_gdf):
    '''

    input_gdf will be in epsg:4326 projection

    '''
    # Get the centroid of the GeoDataFrame to determine the UTM zone
    centroid = input_gdf.geometry.unary_union.centroid

    # Determine the UTM CRS zone based on the centroid
    utm_zone = f'+proj=utm +zone={int((centroid.x + 180) / 6) + 1} +datum=WGS84 +units=m +no_defs'

    # Convert the GeoDataFrame to the UTM projection
    gdf_utm = input_gdf.to_crs(utm_zone)

    # Calculate area in UTM projection and add it to the input file
    input_gdf['area'] = gdf_utm.geometry.area

    #Get count of polygons which are less than 50sqm 4
    less_than_50sqm_count = len(input_gdf[input_gdf['area'] < 50])

    #Keep polygons with area greater than 50 sqm
    input_gdf = input_gdf[input_gdf['area'] > 50]

    return input_gdf, less_than_50sqm_count


def remove_multipolygos_and_simplify(gdf):
    '''
    gdf: Input will be in epsg:4326 projection

    '''

    multi_polygon_count = 0
    new_entries = []
    remove_idx = []

    for idx, row in gdf.iterrows():
        geom = row.geometry
        if isinstance(geom, MultiPolygon):
            multi_polygon_count += 1
            remove_idx.append(idx)
            # Convert MultiPolygon to individual Polygons
            polygons = [Polygon(poly) for poly in geom]

            # Create new entries for all Polygons in the MultiPolygon
            for polygon in polygons:
                new_entry = gdf.iloc[idx].copy()
                new_entry['geometry'] = polygon
                new_entries.append(new_entry)

    #drop the multipolyogn geometries from existing table
    print('remove_idx : ', remove_idx)

    gdf = gdf.drop(index = remove_idx)

    if new_entries:
        # Append new entries for individual Polygons to the GeoDataFrame
        new_gdf = gpd.GeoDataFrame(new_entries, crs=gdf.crs)
        gdf = gpd.GeoDataFrame(pd.concat([gdf, new_gdf]), crs=gdf.crs)

    # Simplify the given geometry to specified distance.
    gdf = gdf.to_crs("EPSG:3857")
    SIMPLIFY_TOLERANCE = 0.25
    gdf['geometry'] = gdf.geometry.simplify(tolerance = SIMPLIFY_TOLERANCE, preserve_topology = True)
    gdf = gdf.to_crs("EPSG:4326")

    return gdf, multi_polygon_count


def filter_farms_inside_vill(fbd_output, vill_uuid):
    '''

    '''
    # Read the input farm boundary file and convert it to EPSG 4326
    gdf = gpd.read_file(fbd_output)
    gdf = gdf.to_crs("EPSG:4326")

    # Dummy DB connection
    db_connection_url = "postgresql://postgres:postgres@localhost:5432/platform_data"
    con = create_engine(db_connection_url)

    query = f"select * from village_data where village_uuid='{vill_uuid}'"
    vill_gdf = gpd.GeoDataFrame.from_postgis(query, con)

    #vill_gdf = gpd.read_file(vill_uuid)

    if vill_gdf.crs.srs != gdf.crs.srs:
        vill_gdf = vill_gdf.to_crs(gdf.crs.srs)

    # Perform the spatial join to get farms within the village boundary
    farms_within_village = gpd.sjoin(gdf, vill_gdf, op='intersects') # try intersects oprator also

    count_of_farm_outside = len(gdf) - len(farms_within_village)

    farms_within_village.reset_index(inplace=True, drop=True)
    farms_within_village = farms_within_village[['geometry']]
    farms_within_village['farm_uuid'] = ''
    for i in range(len(farms_within_village)):
        farms_within_village['farm_uuid'][i] = str(uuid.uuid4())

    farms_within_village['village_uuid'] = vill_uuid

    #gdf.to_file(fbd_output)

    return farms_within_village, count_of_farm_outside



def main(input_farm_bound, vill_uuid):

    # filtering frams based on the village UUID. Output will be farms inside village (in epsg:4326)
    farms_inside_village, count_of_farm_outside = filter_farms_inside_vill(input_farm_bound, vill_uuid)

    # fix invalid geometries
    fixed_geometry_output, count_after_fix_geometry = fix_invalid_geometries(farms_inside_village)

    # convert multipolygon geometry to polygon geometry and simplify the shapefile
    single_polygons_gdf, multi_polygon_count = remove_multipolygos_and_simplify(fixed_geometry_output)

    # calculate area in UTM projection and remove farms having area less than 50sqm
    farms_with_area_gte50sqm, less_than_50sqm_count = calculate_area_in_utm(single_polygons_gdf)

    return farms_with_area_gte50sqm, less_than_50sqm_count, count_after_fix_geometry, count_of_farm_outside, multi_polygon_count


farms_with_area_gte50sqm, less_than_50sqm_count, count_after_fix_geometry, count_of_farm_outside, multi_polygon_count  = main('/mnt/c/Users/shubh/Downloads/testing_farm_functions/farms.shp', 'vill_uuid')
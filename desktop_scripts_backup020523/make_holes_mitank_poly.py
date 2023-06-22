from shapely.geometry import shape, mapping
from shapely.geometry import Polygon, MultiPolygon
from shapely.ops import cascaded_union, unary_union
import numpy as np
import geopandas as gpd
import pandas as pd


def groupby_multipoly(df, by, aggfunc="first"):
    data = df.drop(labels=df.geometry.name, axis=1)
    aggregated_data = data.groupby(by=by).agg(aggfunc)

    # Process spatial component
    def merge_geometries(block):
        return unary_union(block.values)

    g = df.groupby(by= by, group_keys=False)[df.geometry.name].agg(
        merge_geometries
    )

    # Aggregate
    aggregated_geometry = gpd.GeoDataFrame(g, geometry=df.geometry.name, crs=df.crs)
    # Recombine
    aggregated = aggregated_geometry.join(aggregated_data)
    aggregated.reset_index()
    return aggregated


gpd_shp = gpd.read_file("C:/Users/VassarGIS/Downloads/missing_depth/missing_depth.shp")

gpd_shp['DEPTH'] = gpd_shp['DEPTH'] + 1
gpd_shp = gpd_shp.set_geometry('geometry')
gpd_shp_s1 = gpd_shp[gpd_shp['SOURCE'] == 'SENTINEL_1']
gpd_shp_s1_dem = gpd_shp[gpd_shp['SOURCE'] == 'SENTINEL1_DEM']



error_count = 0

#def make_holes(gpd_shp_s1_dem):
modified_s1_dem_list = []
MITANK_ID = gpd_shp_s1_dem.MITANK_ID.unique()
for mi_tank in MITANK_ID:
    mi_tank_s1_dem = gpd_shp_s1_dem[gpd_shp_s1_dem['MITANK_ID'] == mi_tank]

    dates = mi_tank_s1_dem.DATE.unique()
    for date in dates:
        mi_tank_s1_dem_date = mi_tank_s1_dem[mi_tank_s1_dem['DATE'] == date]
        mi_tank_s1_dem_date = mi_tank_s1_dem_date.sort_values('DEPTH')

        #print(mi_tank_s1_dem_date)
        try:
            mi_tank_s1_dem_date = groupby_multipoly(mi_tank_s1_dem_date,['MITANK_ID', 'DEPTH'])
            mi_tank_s1_dem_date = mi_tank_s1_dem_date.reset_index()
            depth_1 = mi_tank_s1_dem_date[mi_tank_s1_dem_date['DEPTH'] == 1].geometry.values[0]
            depth_2 = mi_tank_s1_dem_date[mi_tank_s1_dem_date['DEPTH'] == 2].geometry.values[0]
            depth_3 = mi_tank_s1_dem_date[mi_tank_s1_dem_date['DEPTH'] == 3].geometry.values[0]

            mod_depth_1 = depth_1.difference(depth_2)
            mod_depth_2 = depth_2.difference(depth_3)

            mod_geom = [mod_depth_1, mod_depth_2, depth_3]

            mi_tank_s1_dem_date['geometry'] = mod_geom

            new_geom = mi_tank_s1_dem_date.copy()
            modified_s1_dem_list.append(new_geom)

        except:
            try:
                print('loop_2')
                mi_tank_s1_dem_date = mi_tank_s1_dem_date.reset_index()
                depth_1 = mi_tank_s1_dem_date[mi_tank_s1_dem_date['DEPTH'] == 1].geometry.values[0]
                depth_2 = mi_tank_s1_dem_date[mi_tank_s1_dem_date['DEPTH'] == 2].geometry.values[0]
                #depth_3 = mi_tank_s1_dem_date[mi_tank_s1_dem_date['DEPTH'] == 3].geometry.values[0]

                mod_depth_1 = depth_1.difference(depth_2)
                #mod_depth_2 = depth_2.difference(depth_3)

                mod_geom = [mod_depth_1, mod_depth_2]

                mi_tank_s1_dem_date['geometry'] = mod_geom

                new_geom = mi_tank_s1_dem_date.copy()
                modified_s1_dem_list.append(new_geom)

            except:
                error_count = error_count + 1
                print(mi_tank_s1_dem_date)
                print(mi_tank_s1_dem_date.DEPTH.unique())
                modified_s1_dem_list.append(mi_tank_s1_dem_date)

df = pd.concat(modified_s1_dem_list, axis= 0)
mod_gpd_shp_s1_dem = gpd.GeoDataFrame(df)
mod_gpd_shp_s1_dem.set_geometry('geometry', inplace = True)



#mod_gpd_shp_s1_dem = make_holes(gpd_shp_s1_dem)

df_merged = mod_gpd_shp_s1_dem.append(gpd_shp_s1, ignore_index=True)

new_gdf = gpd.GeoDataFrame(df_merged)
new_gdf.set_geometry('geometry', inplace = True)



new_gdf.to_file("C:/Users/VassarGIS/Downloads/OD_depth_holes/OD_depth_holes_processed_220223.gpkg", "GPKG")


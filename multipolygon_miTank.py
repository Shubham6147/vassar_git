import glob 
import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon


def groupby_multipoly(df, by, aggfunc="first"):
    data = df.drop(labels=df.geometry.name, axis=1)
    aggregated_data = data.groupby(by=by).agg(aggfunc)

    # Process spatial component
    def merge_geometries(block):
        return MultiPolygon(block.values)

    g = df.groupby(by= by, group_keys=False)[df.geometry.name].agg(
        merge_geometries
    )

    # Aggregate
    aggregated_geometry = gpd.GeoDataFrame(g, geometry=df.geometry.name, crs=df.crs)
    # Recombine
    aggregated = aggregated_geometry.join(aggregated_data)
    aggregated.reset_index()
    return aggregated



shp_files = glob.glob('/mnt/d/grass_test/TG_Jan_Data_2/*.shp')

for shp_file in shp_files:
    file = gpd.read_file(shp_file)
    
    sen1_data = file[gpd_shp['SOURCE'] == 'SENTINEL_1']
    sen1_dem_data = file[gpd_shp['SOURCE'] == 'SENTINEL1_DEM']
    
    multi_sen1_data = groupby_multipoly(sen1_data,['MITANK_ID', 'DEPTH'])
    multi_sen1_data = multi_sen1_data.reset_index()
    
    multi_sen1_dem_data = groupby_multipoly(sen1_dem_data,['MITANK_ID', 'DEPTH'])
    multi_sen1_dem_data = multi_sen1_dem_data.reset_index()
    
    
    df_merged = multi_sen1_dem_data.append(multi_sen1_data, ignore_index=True)

    new_gdf = gpd.GeoDataFrame(df_merged)
    new_gdf.set_geometry('geometry', inplace = True)
    
    file2.to_file(new_gdf)
    

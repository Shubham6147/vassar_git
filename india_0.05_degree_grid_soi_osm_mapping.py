import geopandas as gpd
import pandas as pd
import fiona

grid_file = gpd.read_file('C:/Users/shubh/Downloads/grid_0.05_india.shp')

grid_file = grid_file[grid_file['topo_OSM_S'].notna()]
grid_file['level_1'] = grid_file['topo_OSM_S'].apply(lambda p: p.split(" ")[0])
grid_file['level_2'] = grid_file['topo_OSM_S'].apply(lambda p: p.split(" ")[1][:2])
grid_file['level_3'] = grid_file['topo_OSM_S'].apply(lambda p: p.split(" ")[1][2])
grid_file['level_4'] = grid_file['topo_OSM_S'].apply(lambda p: p.split(" ")[1][3:])

all_merged = []

i = 1

for unque_id in grid_file['topo_OSM_S'].unique():
    if i == 10:
        break

    world = grid_file[grid_file['topo_OSM_S'] == unque_id]
    world['cen_lat'] = world['lat']
    world['cen_lon'] = world['lon']
    #Create some data:
    #world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    #world['centroid_column'] = world.centroid
    #world = world.set_geometry('centroid_column')
    #world.drop(['pop_est', 'name', 'iso_a3', 'gdp_md_est','geometry'], axis=1, inplace=True)

    #Create an x coordinate column
    #world['x'] = world['centroid_column'].apply(lambda p: p.x)
    #world['y'] = world['centroid_column'].apply(lambda p: p.y)

    #Set x column as index and sort:
    world = world.set_index('lon').sort_index()
    world['rank_1'] = (world.groupby('cen_lat').cumcount()+1).astype(str)#.str.zfill(2)

    #Set x column as index and sort:
    world = world.set_index('lat').sort_index()
    world['rank_2'] = (world.groupby('cen_lon').cumcount()+1).astype(str)#.str.zfill(2)

    world['rank'] = world['rank_1'] + world['rank_2'] # (world.groupby('y').cumcount()+1).astype(str)#.str.zfill(2)

    #Set x column as index and sort:
    #world['x'] = world['centroid_column'].apply(lambda p: p.x)
    world = world.set_index('rank').sort_index()
    index_ing = range(1, len(world)+1)
    world['rank_final'] = index_ing


    all_merged.append(world)
    #i = i+1

final_grid = pd.concat(all_merged)

final_grid = gpd.GeoDataFrame(final_grid)
final_grid.reset_index(inplace=True)
#final_grid.drop('centroid_column',axis=1, inplace= True)
final_grid = final_grid.set_geometry('geometry')

with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):

    final_grid.to_file('C:/Users/shubh/Downloads/grid_0.05_india_step1.shp')
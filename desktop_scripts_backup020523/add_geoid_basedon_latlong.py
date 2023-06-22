import geopandas as gpd
import uuid


input_file = r"C:\Users\VassarGIS\Downloads\OD_new_mitank_from_pt_multi_till_Feb02\230203_OD_new_mitank .shp"
gdf = gpd.read_file(input_file)

#gdf = gdf.astype({'lat':'string', 'long':'string'})
gdf['tank_geoid'] = ''
gdf['mitank_uuid'] = ''
for index, row in gdf.iterrows():
    lat = str(format(row['cen_y'], '.4f'))
    long = str(format(row['cen_x'], '.4f'))
    tank_geoid = long[:2]+ long[3:8] + lat[:2]+ lat[3:8]

    gdf.iloc[index, gdf.columns.get_loc('tank_geoid')] = tank_geoid
    gdf.iloc[index, gdf.columns.get_loc('mitank_uuid')] = str(uuid.uuid4())
    print(tank_geoid)

gdf.to_file(input_file)

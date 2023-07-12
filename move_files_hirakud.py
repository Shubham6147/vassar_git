import geopandas as gpd
import os
import shutil

row_file = gpd.read_file('C:/Users/shubh/Downloads/attabira_Ayacut_boundary/attabira_Ayacut_boundary_grid_150m.shp')

not_available_uuid = []

for index, row in row_file.iterrows():
    img_file = f"/media/vassarml/HDD/shubham/hirakud/{row['GRID_UUID']}.tif"

    dst_path = os.path.join('/media/vassarml/HDD/shubham/hirakud2/',os.path.basename(img_file))
    if not os.path.exists(img_file):
        print('----file is not availbale----')
        not_available_uuid.append(row['GRID_UUID'])
        print(row['GRID_UUID'])
    else:
        shutil.copy(img_file, dst_path)

print(not_available_uuid)




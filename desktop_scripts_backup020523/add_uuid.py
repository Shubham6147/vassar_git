##
##import uuid
##import geopandas as gpd
##
##file = r"C:\Users\VassarGIS\Downloads\Pranay_delet\Odisha_Major_Ayacut_Update_SubProject.shp"
##outfile = r"C:\Users\VassarGIS\Downloads\Pranay_delet\Odisha_Major_Ayacut_Update_SubProject_uuid.shp"
##shp_data = gpd.read_file(file)
##shp_data['uuid'] = ""
####shp_data['geoid'] = ""
####print(shp_data['District'])
##
##for i in range(len(shp_data['SubProject'])):
##    print(i)
##    shp_data['uuid'][i] = str(uuid.uuid4())
####    lat = str(shp_data['Lat'][i])
####    lat = lat[:2] + lat[3:7]
####    long = str(shp_data['Long'][i])
####    long = long[:2] + long[3:7]
####    geoid = long+lat
####    shp_data['geoid'][i] = geoid
##
##shp_data.to_file(outfile)
##



import uuid
import pandas as pd

file = r"C:\Users\VassarGIS\Downloads\Rengali_KamakhyaNagar_LBC_Metadata_updated.csv"
outfile = r"C:\Users\VassarGIS\Downloads\Rengali_KamakhyaNagar_LBC_Metadata_updated_uuid.csv"
shp_data = pd.read_csv(file)
shp_data['uuid'] = ""
##shp_data['geoid'] = ""
##print(shp_data['District'])

for i in range(len(shp_data['Canal Name (As per schematic diagram)'])):
    print(i)
    shp_data['uuid'][i] = str(uuid.uuid4())

##    lat = str(shp_data['Lat'][i])
##    lat = lat[:2] + lat[3:7]
##    long = str(shp_data['Long'][i])
##    long = long[:2] + long[3:7]
##    geoid = long+lat```````
##    shp_data['geoid'][i] = geoid

#shp_data.to_csv(outfile)

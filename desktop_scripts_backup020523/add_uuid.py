import uuid
import geopandas as gpd
import fiona

file = r"C:/Users/shubh/Downloads/farm_boundaries/Farm_Boundaries_4villages_merge.shp"
outfile = r"C:/Users/shubh/Downloads/farm_boundaries/Farm_Boundaries_4villages_merge_uuid.shp"
shp_data = gpd.read_file(file)
shp_data['uuid'] = ""
#shp_data['geoid'] = ""
#print(shp_data['District'])

for i in range(len(shp_data)):
    print(i)
    shp_data['uuid'][i] = str(uuid.uuid4())

with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
    shp_data.to_file(outfile)


##
##   #lat = str(shp_data['Lat'][i])
##   #lat = lat[:2] + lat[3:7]
##   #long = str(shp_data['Long'][i])
##   #long = long[:2] + long[3:7]
##   #geoid = long+lat
##   #shp_data['geoid'][i] = geoid


##import uuid
##import pandas as pd
##
##file = r"C:\Users\VassarGIS\Downloads\Rengali_KamakhyaNagar_LBC_Metadata_updated.csv"
##outfile = r"C:\Users\VassarGIS\Downloads\Rengali_KamakhyaNagar_LBC_Metadata_updated_uuid.csv"
##shp_data = pd.read_csv(file)
##shp_data['uuid'] = ""
####shp_data['geoid'] = ""
####print(shp_data['District'])
##
##for i in range(len(shp_data['Canal Name (As per schematic diagram)'])):
##    print(i)
##    shp_data['uuid'][i] = str(uuid.uuid4())
##
####    lat = str(shp_data['Lat'][i])
####    lat = lat[:2] + lat[3:7]
####    long = str(shp_data['Long'][i])
####    long = long[:2] + long[3:7]
####    geoid = long+lat```````
####    shp_data['geoid'][i] = geoid
##
###shp_data.to_csv(outfile)

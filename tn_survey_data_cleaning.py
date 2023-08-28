import geopandas as gpd
from functools import reduce
from fuzzywuzzy import process
import pandas as pd
import fiona


layer_pt_path = r"C:/Users/shubh/Downloads/Final_Karera_GT_312/Final_Karera_GT_312.shp"
#picture_pt_path = r"C:\Users\shubh\Downloads\Ground_truth\Ground_truth\Villupuram Shapefiles\photos.shp"

flag = ''


#picture_pt = gpd.read_file(picture_pt_path)
layer_pt = gpd.read_file(layer_pt_path)
crop_classes = pd.read_csv(r"C:\Users\shubh\Downloads\Ground_truth\crop_class.csv")


replace_list = ['Point ', 'point ', 'Ponit ']

#picture_pt['ID'] = picture_pt['REMARKS'].map(lambda x: reduce(lambda s, sub: s.replace(sub, ""), replace_list, x))

#picture_pt['ID'] = picture_pt['REMARKS']#.map(lambda x:


layer_pt["crop_name"] = ""
layer_pt["crop_id"] = ""
#layer_pt["PATH"] = ""
#layer_pt['source'] = ""

for idx, row in layer_pt.iterrows():
    #print('Matching %s with'%(uniq_name), list(filtered_2011.values))
    #match = process.extractOne(str(row['_REMARKS']), list(crop_classes['display_name'].values))
    match = process.extractOne(str(row['Crop_Categ']), list(crop_classes['display_name'].values))

    if match[1] > 60:
        print('%s \t %s \t confidence:%d.' %
              (row['Crop_Categ'], match[0], match[1]))

        #print('Replacing with', match[0])

        layer_pt.loc[idx, 'crop_name'] = match[0]
        crop_idx = crop_classes[crop_classes['display_name']== match[0]].index
        layer_pt.loc[idx, 'crop_id'] = str(crop_classes.loc[crop_idx[0], 'location_id'])

##    match = process.extractOne(str(row['_ID']), list(picture_pt['ID'].values))
##
##    if match[1] > 95:
##        print('%s \t %s \t confidence:%d.' %
##              (row['_ID'], match[0], match[1]))
##
##
##        idx_2001 = picture_pt[picture_pt['ID'] == match[0]].index
##        layer_pt.loc[idx, 'PATH'] = picture_pt.loc[idx_2001[0], 'PATH']



    if flag in ['Timmasara', 'Kollankovil']:


        layer_pt['source'] = layer_pt['_REMARKS'].apply(lambda x: 'gw' if ' gw' in str(x).lower() else 'river' if ' river' in str(x).lower() else 'canal' if ' canal' in str(x).lower() else '')




with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
    layer_pt.to_file(layer_pt_path[:-4] + '_UPDATE.shp')

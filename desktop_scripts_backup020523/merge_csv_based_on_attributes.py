import pandas as pd

df1 = pd.read_excel("C:\Users\VassarGIS\Downloads\Misssing_data_Odisha_Kharif_2021-22_Crop_area.csv")
df2 = pd.read_csv("C:\Users\VassarGIS\Downloads\Merge_crop_data.csv")
#a = zip(df2['Block'],df2['Block_new'])
#a = dict(a)

#df1['Block_new'] = df1['Block'].map(a)
df = pd.merge(df1, df2, on='Name Of The Crop', how='left')
df.to_csv('C:\Users\VassarGIS\Downloads\Misssing_data_Odisha_Kharif_2021-22_Crop_area_merged.csv')

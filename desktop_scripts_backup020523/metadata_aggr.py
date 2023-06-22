## importing python library
import pandas as pd
from pandas.core.reshape.merge import merge
import geopandas as gpd
# print(pd.__version__) #-->1.3.5
'''
path1 = '/home/user/Desktop/LiveWork/task3/input/final.csv'  #final.csv
path2 = '/home/user/Desktop/LiveWork/task3/input/merged.csv' # merged and filtered

df = pd.read_csv(path1)
df2 = pd.read_csv(path2)
# print(df.shape)
# print(df2.shape)

#### new df having onlu needed columns
df2 = df2[['uuid', 'max_area', 'capacity_x', 'ayacut_are']].copy()
# print(df2.shape)

### Adding 'max_area', 'capacity_x', 'ayacut_are'  to new df
merged_df = pd.merge(df, df2, left_on='uuid', right_on='uuid',how='left')
# print(merged_df.shape)
# merged_df.to_csv('merged.csv')

####### putting 0 in place of nan value so that addition won't have any problem
merged_df['max_area'] = merged_df['max_area'].fillna(0)
merged_df['capacity_x'] = merged_df['capacity_x'].fillna(0)
merged_df['ayacut_are'] = merged_df['ayacut_are'].fillna(0)

# x = merged_df['ayacut_are'].values[19517]
# print(x)


'''
    #35396  having only mitank(total=35425)   and   total=35962
'''


##################### Function #######################

def Sum_Count(df1, parent, child):
    for index, row in parent.iterrows():
        uuid = row['uuid']
        x = df1[(df1.parent_uuid == uuid) & (df1['uuid_type'] == child)]
        df1.at[index, 'max_area'] = x['max_area'].sum()
        df1.at[index, 'capacity_x'] = x['capacity_x'].sum()
        df1.at[index, 'ayacut_are'] = x['ayacut_are'].sum()
    return df1

def Sum_Count(df1, parent, child):
    for index, row in parent.iterrows():
        uuid = row['uuid']
        x = df1[(df1.parent_uuid == uuid) & (df1['uuid_type'] == child)]
        df1.at[index, 'max_area'] = x['max_area'].sum()
        df1.at[index, 'capacity_x'] = x['capacity_x'].sum()
        df1.at[index, 'ayacut_are'] = x['ayacut_are'].sum()
    return df1

df1 = merged_df

#####  admin
df1 = Sum_Count(df1, df1[df1.uuid_type == 'mandal'], 'mitank')
df1 = Sum_Count(df1, df1[df1.uuid_type == 'district'], 'mandal')
df1 = Sum_Count(df1, df1[df1.uuid_type == 'state'], 'district')

#####  basin
df1 = Sum_Count(df1, df1[df1.uuid_type == 'subbasin'], 'mitank')
df1 = Sum_Count(df1, df1[df1.uuid_type == 'basin'], 'subbasin')
df1 = Sum_Count(df1, df1[df1.uuid_type == 'state'], 'basin')

#####  project
df1 = Sum_Count(df1, df1[df1.uuid_type == 'command_mandal'], 'mitank')
df1 = Sum_Count( df1, df1[df1.uuid_type == 'command_district'], 'command_mandal')
df1 = Sum_Count( df1, df1[df1.uuid_type == 'sub_command_area'], 'command_district')
df1 = Sum_Count(df1, df1[df1.uuid_type == 'command_area'], 'sub_command_area')
df1 = Sum_Count(df1, df1[df1.uuid_type == 'state'], 'command_area')

# print( df1[merged_df.uuid_type == 'mandal'])

# df1.to_csv('result.csv')
print(df1)
print("Done!!")


'''
'''
 ADMIN: MITANK,MANDAL,DISTRICT,STATE
 BASIN: MITANK,subbasin,BASIN,STATE
 PROJECT: MITANK,command_mandal,command_district,sub_command_area,command_area,STATE

 mitank
 state
 subbasin
 mandal
 command_mandal
 sub_command_area
 basin
 district
 command_area
 command_district

'''

gdf =gpd.read_file(r"C:\Users\VassarGIS\Downloads\OD_new_mitank_from_pt_multi_till_Feb02\230203_OD_new_mitank_V4.shp")
#df= pd.read_csv('C:/Users/VassarGIS/Downloads/drive-download-20230102T053005Z-001/TN_mitank_maxvol.csv')

gdf1 = gdf.copy()

gdf1.rename(columns={'area':'max_area'}, inplace = True)

gdf1 = gdf1[['mitank_uui','capacity','max_area','district_u','block_uuid','state_uuid']]
st = gdf1.state_uuid.unique()
di = gdf1.district_u.unique()
ma= gdf1.block_uuid.unique()
#vi = gdf1.village_uu.unique()
mi = gdf1.mitank_uui.unique()

#uuid, parent_uuid, capacity, max_area, count, ayacut_area, uuid_type,hierarchy_type



uuid =[]
parent_uuid=[]
capacity= []
max_area=[]
count = []
ayacut_area =[]
uuid_type =[]
hierarchy_type=[]

#gdf1['ayacut'] = gdf1['ayacut'].fillna(0)

for i in st:
    if i is not None:
        uuid.append(i)
        parent_uuid.append(gdf1[gdf1.state_uuid==i].state_uuid.unique()[0])
        capacity.append(gdf1[gdf1.state_uuid==i].capacity.sum())
        max_area.append(gdf1[gdf1.state_uuid==i].max_area.sum())
        count.append(len(gdf1[gdf1.state_uuid==i]))
        #ayacut_area.append(gdf1[gdf1.uuid==i].ayacut.astype('float').sum())
        uuid_type.append('state')
        hierarchy_type.append('admin')


for i in di:
    if i is not None:
        uuid.append(i)
        parent_uuid.append(gdf1[gdf1.district_u==i].state_uuid.unique()[0])
        capacity.append(gdf1[gdf1.district_u==i].capacity.sum())
        max_area.append(gdf1[gdf1.district_u==i].max_area.sum())
        count.append(len(gdf1[gdf1.district_u==i]))
        #ayacut_area.append(gdf1[gdf1.uuid==i].ayacut.astype('float').sum())
        uuid_type.append('district')
        hierarchy_type.append('admin')

for i in ma:
    if i is not None:
        uuid.append(i)
        parent_uuid.append(gdf1[gdf1.block_uuid==i].district_u.unique()[0])
        capacity.append(gdf1[gdf1.block_uuid==i].capacity.sum())
        max_area.append(gdf1[gdf1.block_uuid==i].max_area.sum())
        count.append(len(gdf1[gdf1.block_uuid==i]))
        #ayacut_area.append(gdf1[gdf1.uuid==i].ayacut.astype('float').sum())
        uuid_type.append('block')
        hierarchy_type.append('admin')

for i in mi:
    if i is not None:
        uuid.append(i)
        parent_uuid.append(gdf1[gdf1.mitank_uui==i].block_uuid.unique()[0])
        capacity.append(gdf1[gdf1.mitank_uui==i].capacity.sum())
        max_area.append(gdf1[gdf1.mitank_uui==i].max_area.sum())
        count.append(len(gdf1[gdf1.mitank_uui==i]))
        #ayacut_area.append(gdf1[gdf1.uuid==i].ayacut.astype('float').sum())
        uuid_type.append('mitank')
        hierarchy_type.append('admin')

df1 = pd.DataFrame()
df1['uuid'] = uuid
df1['parent_uuid'] = parent_uuid
df1['capacity'] = capacity
df1['max_area'] = max_area
df1['count'] = count
#df1['ayacut_area'] = ayacut_area
df1['uuid_type'] = uuid_type
df1['hierarchy_type'] = hierarchy_type
df1['state_code'] = 'd19a5290-2e40-494a-83d2-98f4c845b1f1'

df1.to_csv(r"C:\Users\VassarGIS\Downloads\OD_new_mitank_from_pt_multi_till_Feb02\OD_mitank_maxvol_V4.csv",index=0)

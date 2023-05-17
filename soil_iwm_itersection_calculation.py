#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      shubh
#
# Created:     22-03-2023
# Copyright:   (c) shubh 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import geopandas as gpd

iwm_grid = gpd.read_file('C:/Users/shubh/Downloads/IWM_GRID_ODisha/IWM_GRID_ODisha.shp')
soil_data = gpd.read_file('C:/Users/shubh/Downloads/Odisha_soil/Odisha_soil_inter.shp')

print(len(soil_data.uuid.unique()))


iwm_grid[['iwm_sal_1', 'iwm_sal_2', 'iwm_sal_3', 'iwm_sal_4','iwm_sal_5', 'iwm_sal_6']] = 0

for iwm_uuid in soil_data.uuid.unique():
    grid_inter = soil_data[soil_data['uuid'] == iwm_uuid]
    grid_inter['area_contri'] = grid_inter['area'] / 29.3

    if grid_inter['area'].sum() > 14.65:

        remainder = 1 - grid_inter['area_contri'].sum()


        grid_inter['contri'] = grid_inter['area_contri'] + grid_inter['area_contri'] * remainder

        grid_inter[['sal_1', 'sal_2', 'sal_3', 'sal_4','sal_5', 'sal_6']] = grid_inter[['sal_1', 'sal_2', 'sal_3', 'sal_4','sal_5', 'sal_6']].fillna(0)

        grid_inter[['sal_1', 'sal_2', 'sal_3', 'sal_4','sal_5', 'sal_6']] =  grid_inter[['sal_1', 'sal_2', 'sal_3', 'sal_4','sal_5', 'sal_6']].astype(str).astype(float)

        grid_inter.loc[:, ['iwm_sal_1', 'iwm_sal_2', 'iwm_sal_3', 'iwm_sal_4','iwm_sal_5', 'iwm_sal_6']] = grid_inter[['sal_1', 'sal_2', 'sal_3', 'sal_4','sal_5', 'sal_6']].to_numpy() * grid_inter[['contri']].to_numpy()


        iwm_grid.loc[iwm_grid['uuid'] == iwm_uuid, ['iwm_sal_1', 'iwm_sal_2', 'iwm_sal_3', 'iwm_sal_4','iwm_sal_5', 'iwm_sal_6']] = grid_inter[['iwm_sal_1', 'iwm_sal_2', 'iwm_sal_3', 'iwm_sal_4','iwm_sal_5', 'iwm_sal_6']].sum().values

    #break
iwm_grid = iwm_grid.to_crs('EPSG:4326')
iwm_grid.to_file('C:/Users/shubh/Downloads/IWM_GRID_ODisha/IWM_GRID_ODisha_sand.shp')

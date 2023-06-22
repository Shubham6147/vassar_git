#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     16-02-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import pandas as pd
import glob



list_csv = glob.glob('F:/CROP_STRESS_AP_PROJECTS/NDMI_AP_PROJECTS/*.csv')

all_files = []

for csv_file in list_csv:
    df_csv = pd.read_csv(csv_file)
    #df_csv['NDVI'] = df_csv['NDMI']/10
    df_csv.drop(['Unnamed: 0','area', 'perimeter', 'layer', 'path'], axis = 1, inplace = True)
    df_2 = df_csv.copy()
    all_files.append(df_2)



all_project_data = pd.concat(all_files, axis = 0)
all_project_data = pd.DataFrame(all_project_data)

all_project_data.to_csv('F:/CROP_STRESS_AP_PROJECTS/NDVI_AP_PROJECTS/AP_Project_wetness_index_230212.csv')

#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     08-03-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os
import glob

file_list = glob.glob("E:/OD_stack_wetness/*.tif")


for img_file in file_list:
    filename = os.path.basename(img_file)

    output_file = 'F:/OD_Sen1_Wetness/mask_final/' + filename

    if filename.split("_")[1] == 'Hirakud':
        print('Hirakud')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/hirakud_agri_fix.shp"

    elif filename.split("_")[1] == 'Indravati':
        print('Indravati')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/indrawati_agri_fix.shp"

    elif filename.split("_")[1] == 'Rengali':
        print('Rengali')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/rangoli_agri_fix.shp"

    elif filename.split("_")[1] == 'Anandapur':
        print('Anandapur')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Anandapur_agri_fix.shp"

    elif filename.split("_")[1] == 'Baitarani':
        print('Baitarani')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Baitarani_agri_fix_cor.shp"

    elif filename.split("_")[1] == 'Lower':
        print('Lower_Indra')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Lower_Indra_agri_fix.shp"

    elif filename.split("_")[1] == 'Potteru':
        print('Potteru')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/potteru_agri_fix.shp"

    elif filename.split("_")[1] == 'Salandi':
        print('Salandi')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Salandi_agri_fix.shp"

    elif filename.split("_")[1] == 'Salki':
        print('Salki')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Salki_agri_fix.shp"

    elif filename.split("_")[1] == 'Subarnarekah':
        print('Subarnarekah')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Subarnarekah_agri_fix.shp"

    elif filename.split("_")[1] == 'Kolab':
        print('Kolab')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Kolab_agri_fix.shp"

    elif filename.split("_")[1] == 'Mahanadi':
        print('Mahanadi')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Mahanadi_agri_fix.shp"

    elif filename.split("_")[1] == 'Rushikulya':
        print('Rushikulya')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/Rushikulya_agri_fix.shp"


    cmd = f'gdalwarp -overwrite -of GTiff -cutline {shp_path} -crop_to_cutline -ot Byte -dstnodata 0 -multi -wo "NUM_THREADS=ALL_CPUS" -co "COMPRESS=DEFLATE" {img_file} {output_file}'
    print(cmd)
    os.system(cmd)


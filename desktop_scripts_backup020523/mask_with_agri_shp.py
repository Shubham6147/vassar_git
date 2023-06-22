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

file_list = glob.glob("F:/OD_Sen2_OPTRAM/*.tif")


for img_file in file_list:
    filename = os.path.basename(img_file)
    output_file = 'F:/OD_Sen2_OPTRAM/mask/' + filename

    if filename.split("_")[1] == 'Hirakud':
        print('Hirakud')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/hirakud_agri_fix.shp"

    elif filename.split("_")[1] == 'Indravati':
        print('Indravati')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/indrawati_agri_fix.shp"

    elif filename.split("_")[1] == 'Rengali':
        print('Rengali')
        shp_path = "F:/Odisha_data/Major_ayacut_lulc/sepreate/rangoli_agri_fix.shp"

    cmd = f'gdalwarp -overwrite -of GTiff -cutline {shp_path} -crop_to_cutline -ot Byte -dstnodata 0 -multi -wo "NUM_THREADS=ALL_CPUS" -co "COMPRESS=DEFLATE" {img_file} {output_file}'
    print(cmd)
    os.system(cmd)


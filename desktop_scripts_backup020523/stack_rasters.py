#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     18-11-2022
# Copyright:   (c) VassarGIS 2022
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import glob
import os

folders = [x[0] for x in os.walk(r"E:/ET_calculation/NRSC_ET0")]  #D:\2021_ET0\10_days
out_folder = r"E:/ET_calculation/NRSC_ET0/stack_2021"


for folder in folders:
    print(folder)
    num = folder.split("\\")[-1]
    vrt_path = folder + f"/{num}.vrt"
    output_path = out_folder + f"/{num}.tif"
    tif_path = folder + "/*.tif"
    cmd = f"gdalbuildvrt -separate {vrt_path} {tif_path}"
    cmd_2 = f'gdalwarp -r near -multi -wo "NUM_THREADS=ALL_CPUS" -co "COMPRESS=LZW" -co "BIGTIFF=YES" {vrt_path} {output_path}'
    os.system(cmd)
    os.system(cmd_2)
    #break


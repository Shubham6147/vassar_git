import glob
import os

folders = [x[0] for x in os.walk(r"H:\Landsat_KTCC_Bimonthly\ALL_WATER_PRED\5year_data")]  #D:\2021_ET0\10_days
out_folder = r"H:\Landsat_KTCC_Bimonthly\ALL_WATER_PRED\02_5year_stack"


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
    

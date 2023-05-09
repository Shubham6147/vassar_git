import os
import pandas as pd
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
from datetime import date
from snap_processing_pipeline import snap_processing


import glob, os
input_path = "D:/snappy_process/251022"
os.chdir(input_path)

for file in glob.glob("*.zip"):
    #print(file)

    zip_name = file.split(".")[0]
    print(zip_name)

    prod_name = zip_name +'.zip'
    print(prod_name)
    input_path = "D:/snappy_process/251022"
    os.chdir(input_path)

    print("downloaded product :" , prod_name )

    zip_file_path = input_path + "/"+ zip_name +'.zip'
    output_folder = 'D:/snappy_process/251022_processing'
    sub_swath = 'IW2'
    firsr_burst = 7 #7 row["IW1_min"]
    last_burst = 9 #row["IW1_max"]

    snap_processing(zip_file_path, output_folder, sub_swath, firsr_burst, last_burst)


                            
    

    

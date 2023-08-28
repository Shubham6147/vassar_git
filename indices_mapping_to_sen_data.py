import os
import glob
import spyndex


def sentinel_s2_l2a(file_path):
    #try:
    # Get the list of files in the folder
    file_list = glob.glob(file_path + '/*.tif')

    # Make prams dict for indices processing
    prams = {
    'A' : [file for file in file_list if 'B01' in file][0],
    'B' : [file for file in file_list if 'B02' in file][0],
    'G' : [file for file in file_list if 'B03' in file][0],
    'R' : [file for file in file_list if 'B04' in file][0],
    'RE1' : [file for file in file_list if 'B05' in file][0],
    'RE2' : [file for file in file_list if 'B06' in file][0],
    'RE3' : [file for file in file_list if 'B07' in file][0],
    'N' : [file for file in file_list if 'B08' in file][0],
    'N2' : [file for file in file_list if 'B8A' in file][0],
    'WV' : [file for file in file_list if 'B09' in file][0],
    'S1' : [file for file in file_list if 'B11' in file][0],
    'S2' : [file for file in file_list if 'B12' in file][0]
    }
    return prams

    #except:
        #pass


param = sentinel_s2_l2a(r"C:\Users\shubh\S2B_60FVG_20190216_0_L2A/")
idx = spyndex.computeIndex("NDVI", param)

#saving idx as tif is pending
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     28-03-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#----------------------------------------------------------------------------
import os
from glob import glob

all_csv_files = []

EXT = '.tif'

PATH = 'F:/OD_Sen2_OPTRAM/10days_final/'


for file in glob("F:/OD_Sen2_OPTRAM/10days_final/**/**/**/*.tif"):
    filepath = os.path.dirname(file) + '/'
    filename = os.path.basename(file)
    out_filename = filename.split('_')[1] + '_irrigation_' + filename.split('_')[-1].replace('-','')

    print (filepath+out_filename)
    os.rename(file, filepath + out_filename)
    #break



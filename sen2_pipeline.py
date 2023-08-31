import time
import os
import sys
import snappy
import glob
from os.path import join


def convert_sec_min(seconds):
    min, sec = divmod(seconds, 60)
    return '%02d:%02d' % (min, sec)

def do_resample(source):
    parameters = snappy.HashMap()
    parameters.put('referenceBandName','B2')
    output = snappy.GPF.createProduct("Resample", parameters, source)
    return output

def do_c2rcc(source):
    parameters = snappy.HashMap()

    parameters.put('salinity', 0.0001)
    parameters.put('elevation' , 15.0)
    parameters.put('useEcmwfAuxData' , 'true')
    parameters.put('outputRtoa' , 'false')
    parameters.put('outputAcReflectance' , 'false')
    parameters.put('outputRhown' , 'false')
    parameters.put('outputKd' , 'false')
    parameters.put('outputUncertainties' , 'false')
    
    
    
    output = snappy.GPF.createProduct("c2rcc.msi", parameters, source)
    return output

def snappy_c2rcc_sen2(zip_file_path, output_folder):

    
    print(zip_file_path)

    zip_file_name = zip_file_path.split("\\")[-1]
    print(zip_file_name)
    
    st = time.time()
    product_s1 = snappy.ProductIO.readProduct(zip_file_path)
	
	
    final_output = output_folder + "/" +zip_file_name.split(".")[0] + "_c2rcc.dim"
    resampled_out = do_resample(product_s1)
    c2rcc_out = do_c2rcc(resampled_out)
    snappy.ProductIO.writeProduct(c2rcc_out,final_output, 'BEAM-DIMAP')

    et = time.time()
    elapsed_time = et - st
    print('Scene processed in:', convert_sec_min(elapsed_time), 'min')



output_folder = "F:/c2rcc_ktcc/c2rcc/"

for zip_file_path in glob.glob("F:/c2rcc_ktcc/*.zip"):
    snappy_c2rcc_sen2(zip_file_path, output_folder)

'''	
if __name__ == '__main__':
    zip_file_path = sys.argv[1]
    output_folder = sys.argv[2]

    snappy_c2rcc_sen2(zip_file_path, output_folder)
'''

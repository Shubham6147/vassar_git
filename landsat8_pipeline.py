import time
import os
import sys
import snappy
from glob import iglob
from os.path import join


def convert_sec_min(seconds):
    min, sec = divmod(seconds, 60)
    return '%02d:%02d' % (min, sec)

def do_c2rcc(source):
    parameters = snappy.HashMap()
    output = snappy.GPF.createProduct("c2rcc.landsat8", parameters, source)
    return output

def snappy_c2rcc(zip_file_path, output_folder):

    
    print(zip_file_path)

    zip_file_name = zip_file_path.split("/")[-1]
    print(zip_file_name)
    
    st = time.time()
    product_s1 = snappy.ProductIO.readProduct(zip_file_path)
	
	
    final_output = output_folder + "/" +zip_file_name.split(".")[0] + "_c2rcc.dim"
	
    c2rcc_out = do_c2rcc(product_s1)
    snappy.ProductIO.writeProduct(c2rcc_out,final_output, 'BEAM-DIMAP')

    et = time.time()
    elapsed_time = et - st
    print('Scene processed in:', convert_sec_min(elapsed_time), 'min')

def main():
	args = sys.argv[1].split(",")
	input_path = args[0]
	output_path = args[1]
	convert_16bit(input_path, output_path)
	mem = memory_usage_resource()
	print('RAM used (in MB):', mem)

	
if __name__ == '__main__':
    zip_file_path = sys.argv[1]
    output_folder = sys.argv[2]

    snappy_c2rcc(zip_file_path, output_folder)

import os
import glob

os.chdir('C:/Users/shubh/Downloads/eto_raster/stack')

for i in range(1,370,10):
    print(i)

    ras_list = []
    for j in range(i,i+10):
        nam = 'C:/Users/shubh/Downloads/eto_raster/Rabbi/' + 'b_'+str(j) + '.tif'

        ras_list.append(nam)

    output_filename = 'C:/Users/shubh/Downloads/eto_raster/stack/Rabbi_et0_' + str(i) + '.tif'
    stack_vrt = f'gdalbuildvrt -separate stack.vrt {(" ").join(ras_list)}'
    print(stack_vrt)

    os.system(stack_vrt)


    merge_vrt = f'gdalwarp -srcnodata -1.7976931348623157e+308 -dstnodata 99 -r near -multi -wo "NUM_THREADS=ALL_CPUS" -co "COMPRESS=LZW" -co "BIGTIFF=YES" stack.vrt {output_filename}'
    print(merge_vrt)
    os.system(merge_vrt)


    break
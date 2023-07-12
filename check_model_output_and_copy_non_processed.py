import glob
import os
import shutil



raw_file_list = glob.glob('/home/vassar/tensorflow/Projects/fbd/training/wbnew/MP/*_0.5m.jp2')


for file_path in raw_file_list:

    print(file_path)
    filename = os.path.basename(file_path)

    out_file = '/home/vassar/tensorflow/Projects/fbd/training/wb_out/' + filename[:-4] + '_M1.tif'
    if not os.path.exists(out_file):
        print('copying')
        destination = os.path.join('/home/vassar/tensorflow/Projects/fbd/training/wbnew/MP/remaining/', os.path.basename(file))

        dest = shutil.copyfile(file_path, destination)

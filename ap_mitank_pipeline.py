from createTiles import downSize
from scalaTransform_and_classification import scalar_transform_and_classification, edge_dilation
from changeprojection import merge_and_change_projection
from get_mitank import creating_small_clipped_rasters
from compute_wsa import area_and_volume


filepath = '/home/ubuntu/vassarlabs/ap#20230203.tif'
date = '20230203'
shape_file='/home/ubuntu/vassarlabs/python_scripts/waterpixelv2/meta_data/ap_water_bodies/4326/AP_MITANKS_Digitize_Waterbodies_Final.shp'

if not os.path.exists('/home/ubuntu/vassarlabs/temp/tiles/'):
    os.makedirs('/home/ubuntu/vassarlabs/temp/tiles/')

if not os.path.exists('/home/ubuntu/vassarlabs/temp/prediction/'):
    os.makedirs('/home/ubuntu/vassarlabs/temp/prediction/')

if not os.path.exists('/home/ubuntu/vassarlabs/temp/prediction/final/'):
    os.makedirs('/home/ubuntu/vassarlabs/temp/prediction/final/')

if not os.path.exists('/home/ubuntu/vassarlabs/temp/temp/'):
    os.makedirs('/home/ubuntu/vassarlabs/temp/temp/')

if not os.path.exists('/home/ubuntu/vassarlabs/temp/out_dir/'):
    os.makedirs('/home/ubuntu/vassarlabs/temp/out_dir/') 

downSize(filepath,'/home/ubuntu/vassarlabs/temp/tiles/',7000,7000)

scalar_transform_and_classification('/home/ubuntu/vassarlabs/temp/tiles/' ,'/home/ubuntu/vassarlabs/shape_files/waterbody_scaler_pammaru_Model5_18102019.bin' , '/home/ubuntu/vassarlabs/shape_files/waterbody_rf_pammaru_Model5_18102019.pkl' , 0.4,'/home/ubuntu/vassarlabs/temp/prediction/')

edge_dilation('/home/ubuntu/vassarlabs/temp/prediction/', 3 ,'/home/ubuntu/vassarlabs/temp/prediction/')

merge_and_change_projection('/home/ubuntu/vassarlabs/temp/prediction/', '/home/ubuntu/vassarlabs/temp/tiles/','/home/ubuntu/vassarlabs/temp/prediction/final/merged.tif','EPSG:4326')

creating_small_clipped_rasters(shape_file, '/home/ubuntu/vassarlabs/temp/tiles/' , '/home/ubuntu/vassarlabs/temp/prediction/final/merged.tif' , date, '/home/ubuntu/vassarlabs/temp/out_dir/')

area_and_volume(shape_file, '/temp/prediction/final/merged.tif', '/home/ubuntu/vassarlabs/temp/tiles/' , '/home/ubuntu/vassarlabs/temp/out_dir/' , date, 'SENTINEL_1', None, '/home/ubuntu/vassarlabs/temp/temp/',
                    float(9.9),float(0.000001), 'MITank_ID', 'Area','geoserver', True, False, 'mitank_raw')


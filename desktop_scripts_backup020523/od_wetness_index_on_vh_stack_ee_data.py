#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     01-03-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import rasterio
import numpy as np
import os, sys
import glob

project_name = 'Indravati'

thre_min= -3000
thre_max= -1000

#date_list = ['20180607','20180619','20180701','20180713','20180725','20180806','20180818','20180830','20180911','20180923','20181005','20181017','20181029','20181110','20181122','20181204','20181216','20181228','20190109','20190121','20190202','20190214','20190226','20190310','20190322','20190403','20190415','20190427','20190509']
#date_list = ['20190614','20190626','20190708','20190720','20190801','20190813','20190825','20190906','20190918','20190930','20191012','20191024','20191105','20191117','20191129','20191211','20191223','20200104','20200116','20200128','20200209','20200221','20200304','20200316','20200328','20200409','20200421','20200503','20200515','20200527']

#date_list = ['20200608','20200620','20200702','20200714','20200726','20200807','20200819','20200831','20200912','20200924','20201006','20201018','20201030','20201111','20201123','20201205','20201217','20201229','20210110','20210122','20210203','20210215','20210227','20210311','20210323','20210404','20210416','20210428','20210510','20210522']
#mid_2021#date_list = ['20210603','20210615','20210627','20210709','20210721','20210802','20210814','20210826','20210907','20210919','20211001','20211013','20211025','20211106','20211118','20211130','20211212','20211224','20220105','20220117','20220129','20220210','20220222','20220306','20220318','20220330','20220411','20220423','20220505','20220517','20220529']

date_list = ["20210608","20210620","20210702","20210714","20210726","20210807","20210819","20210831","20210912","20210924","20211006","20211018","20211030","20211111","20211123","20211205","20211217","20211229","20220110","20220122","20220203","20220215","20220227","20220311","20220323","20220404","20220416","20220428","20220510","20220522"]

raster_path = r"F:\Odisha_S1\indravati\mosaic_indravati.tif"

agri_mask = r"F:\Odisha_S1\indravati\agri_mask_indravati.tif"

data = rasterio.open(raster_path).read()
mask_data = rasterio.open(agri_mask).read()

for no_bands in range(data.shape[0]):

    sensitivity = thre_min - thre_max # -30 - -10

    vh_data = data[no_bands,:,:].reshape((1, data.shape[1], data.shape[2]))

    wetness_index = ((thre_min - vh_data) / sensitivity) *100


    wetness_index[vh_data == 0] = 0
    wetness_index[wetness_index>100] = 100
    wetness_index[wetness_index<0] = 0

    wetness_index = np.round(wetness_index)

    wetness_index = np.reshape(wetness_index, (1, data.shape[1], data.shape[2]))

    wetness_index = wetness_index + 1

    wetness_index = wetness_index * mask_data


    print(wetness_index.shape)


    wetness_index = wetness_index.astype(np.byte)
    wetness_index[wetness_index>100] = 100
    wetness_index[wetness_index == 0] = 125

    with rasterio.open(raster_path) as dataset:
        meta_data = dataset.meta


    output_path = 'F:/Odisha_data/wetness_index/indravati/' + project_name + "_"+ date_list[no_bands]+ '.tif'

    new_dataset = rasterio.open(
        output_path,
        'w',
        driver='GTiff',
        height=meta_data['height'],
        width=meta_data['width'],
        count=wetness_index.shape[0],
        dtype=np.byte,
        crs=meta_data['crs'],
        compress='DEFLATE',
        nodata = 125,
        transform=meta_data['transform']
    )
    new_dataset.write(wetness_index.astype(np.byte))
    new_dataset.close()






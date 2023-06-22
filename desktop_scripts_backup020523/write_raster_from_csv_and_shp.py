#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      VassarGIS
#
# Created:     10-04-2023
# Copyright:   (c) VassarGIS 2023
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import numpy as np
import geopandas as gpd
import pandas as pd
import rasterio
from rasterio import transform
from rasterio import features
from rasterio.enums import Resampling




shp_fn = r"F:\TN_6vill\zonal_statistics\shp\KARUNGADU_field_boundary_vill_UUID_farmUUID\KARUNGADU_field_boundary_vill_UUID_farmUUID.shp"
csv_fn = r"F:\TN_6vill\wetness\2017_vh\KARUNGADU_field_boundary_vill_UUID_farmUUID_S1_VH_17.csv"

out_fn = 'F:/TN_6vill/cor_data/tif/KARUNGADU_field_boundary_vill_UUID_farmUUID_VH_med_2017.tif'
rst_fn = r"F:\TN_6vill\TN_6vill_NDMI_stack\TN_6vill_NDMI_stack_L1_16-18_6.tif"

farms = gpd.read_file(shp_fn)
data_ndvi = pd.read_csv(csv_fn)

df_joined = pd.merge(farms, data_ndvi, how='inner', on = 'Field_UUID')

gdf_joined =  gpd.GeoDataFrame(df_joined)
gdf_joined =  gdf_joined.set_geometry('geometry')


rst = rasterio.open(rst_fn)
meta = rst.meta.copy()
meta.update(compress='lzw')
meta.update(dtype='float64')


##upscale_factor = 1/2
##
##with rasterio.open(rst_fn) as dataset:
##
##    # resample data to target shape
##    data = dataset.read(
##        out_shape=(
##            dataset.count,
##            int(dataset.height * upscale_factor),
##            int(dataset.width * upscale_factor)
##        ),
##        resampling=Resampling.bilinear
##    )
##
##    # scale image transform
##    updated_transform = dataset.transform * dataset.transform.scale(
##        (dataset.width / data.shape[-1]),
##        (dataset.height / data.shape[-2])
##    )
##


meta.update(dtype='float64')
NDVI_filter_col = [col for col in gdf_joined if col.startswith('VH')]
meta.update(count=len(NDVI_filter_col))


with rasterio.open(out_fn, 'w+', **meta) as out:
    out_arr = out.read(1)


    for i in range(len(NDVI_filter_col)):
        # this is where we create a generator of geom, value pairs to use in rasterizing
        shapes = ((geom,value) for geom, value in zip(gdf_joined.geometry, gdf_joined[NDVI_filter_col[i]]))

        burned = features.rasterize(shapes=shapes, fill=0, out=out_arr, transform=out.transform)
        out.write_band(i+1, burned)
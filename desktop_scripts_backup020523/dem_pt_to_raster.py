import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point, Polygon
from shapely.ops import split
import numpy as np
from scipy.interpolate import griddata
import shapefile
import glob, os

from osgeo import gdal, gdal_array, osr

def Create_surface(input_point, output_surface):
    point_shp = shapefile.Reader(input_point)

    shapes = point_shp.shapes()
    point = np.empty((len(shapes),2))
    point[:,0] = [shape.points[0][0] for shape in shapes]
    point[:,1] = [shape.points[0][1] for shape in shapes]

    records = point_shp.records()
    values = [record[0] for record in records]

    '''
    ##Vertex extraction to the Area of Interest
    compDf = gpd.GeoDataFrame()
    compDf['geometry']=None
    i=0


    for index, row in point_shp.iterrows():
        #index counter
        if index % 1000 == 0:
            print('Processing polylines_'+str(index)+'/n')
        if row.geometry!=None: #Check for false geometries
            try:
                simpRow = row.geometry
                for coord in simpRow.coords:
    ##                print(coord)
                    compDf.loc[i]=str(row.POINTID) #Assign values to the dataframe
                    compDf.loc[i,'Easting']=coord[0]
                    compDf.loc[i,'Northing']=coord[1]
                    compDf.loc[i,'Elevation']=row.GRID_CODE

    ##                print(compDf.loc[i,'Easting'])
    ##                print(compDf.loc[i,'Northing'])
            except ValueError: pass
    print("Done")


    point = compDf['Easting','Northing'].values
    print(point)
    #From the dataFrame
    ##points = compDf[['Easting','Northing']].values
    '''

    #Assign the raster eresoulution
    ##rasterRes = 0.000089831528
    rasterRes = 0.00004491576
    geom = [min(point[:,0]),min(point[:,1]),max(point[:,0]),max(point[:,1])]
    #geom_bound = geom
    #Get the Area of Interest dimensions and number of rows / cols
    #print(geom_bound)
    xDim = geom[2]-geom[0]
    yDim = geom[3]-geom[1]
    print('Raster X Dim: %.2f, Raster Y Dim: %.2f'%(xDim,yDim))
    nCols = xDim / rasterRes
    nRows = yDim / rasterRes
    print('Number of cols:  %.2f, Number of rows: %.2f'%(nCols,nRows)) #Check if the cols and row don't have decimals
    ##
    ###We create an array on the cell centroid
    grid_y, grid_x = np.mgrid[geom[1]+rasterRes/2:geom[3]-rasterRes/2:nRows*1j,
                             geom[0]+rasterRes/2:geom[2]+rasterRes/2:nCols*1j]

    mtop = griddata(point, values, (grid_x, grid_y), method='cubic')

    #Raster generation
    geotransform = [geom[0],rasterRes,0,geom[1],0,rasterRes] #[xmin,xres,0,ymax,0,-yres]
    raster = gdal.GetDriverByName('GTiff').Create(output_surface,int(nCols),int(nRows),1,gdal.GDT_Float64)
    raster.SetGeoTransform(geotransform)

    srs=osr.SpatialReference()
    srs.ImportFromEPSG(4326)

    raster.SetProjection(srs.ExportToWkt())
    raster.GetRasterBand(1).WriteArray(mtop)
    del raster

import rasterio
import numpy as np

def data_cor(inras, outras):
    ras = rasterio.open(inras).read()
##    ras[ras>1000] = 0
    ras[ras<0] = 0

    ras = np.nan_to_num(ras, nan=0)

    with rasterio.open(inras) as dataset:
        meta_data = dataset.meta
    new_dataset = rasterio.open(
    outras,
    'w',
    driver='GTiff',
    height=meta_data['height'],
    width=meta_data['width'],
    count=ras.shape[0],
    dtype=ras.dtype,
    crs=meta_data['crs'],
    compress='DEFLATE',
    transform=meta_data['transform'])
    new_dataset.write(ras)
    new_dataset.close()

##f = 'E:/ESA_DEM/Odisha/tg_dem_area1_filled_geo_point.shp'
##filename = 'E:/ESA_DEM/Odisha/TG_dem_area1_point_interpolate.tif'
##Create_surface(f, filename)
f_list = sorted(glob.glob(r'F:/TN_DEM/shp/*.shp'))

print(len(f_list))

for f in f_list:
    filename = f[:-4] + '.tif'
    filename_cor = f[:-4] + '_cor.tif'
    print(f)
    Create_surface(f, filename)
    data_cor(filename, filename_cor)
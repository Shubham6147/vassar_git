import uuid
import geopandas as gpd
import fiona
import numpy as np
from shapely.geometry import Polygon

aoi = gpd.read_file(r'D:/aus_v2/iwm_0.001_aus_uuid_part1_north_selected.shp')




for index, row in aoi.iterrows():
    polygons = []
    uuid_list = []

    xmin, ymin, xmax, ymax = row.geometry.bounds

    length = 0.001
    wide = 0.001

    cols = list(np.arange(xmin, xmax, wide))
    rows = list(np.arange(ymin, ymax, length))

    #shp_data['uuid'][i] = str(uuid.uuid4())



    for x in cols[:-1]:
        for y in rows[:-1]:
            uuid_id = str(uuid.uuid4())

            uuid_list.append(uuid_id)
            polygons.append(Polygon([(x,y), (x+wide, y), (x+wide, y+length), (x, y+length)]))

            #id_aoi = id_aoi + 1

    #break

    out_filename = "D:/aus_v2/iwm_0.01/iwm_0.001_aus_uuid_part1_north_" + row.uuid + ".shp"

    grid = gpd.GeoDataFrame({'uuid': uuid_list, 'geometry':polygons})
    grid['iwm_uuid'] = row.uuid
    grid = grid.set_crs(aoi.crs)


    with fiona.Env(OSR_WKT_FORMAT="WKT2_2018"):
        grid.to_file(out_filename)
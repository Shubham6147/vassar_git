import rasterio
import glob
import pandas as pd
import geopandas as gpd

files = glob.glob(r"C:\Users\VassarGIS\Downloads\google_jag\*_vill3_*.tif")
final = []
for filee in files:

    with rasterio.open(filee) as src:
        bounds = src.bounds

    from shapely.geometry import box
    geom = box(*bounds)

    import geopandas as gpd
    df = gpd.GeoDataFrame({"name":filee.split('\\')[-1],"geometry":[geom]})
    df.crs = src.crs
    final.append(df)

final_df = pd.concat(final)
final_df = gpd.GeoDataFrame(final_df)
final_df.to_file(r"C:\Users\VassarGIS\Downloads\google_jag\vill3.shp")

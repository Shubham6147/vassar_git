import rasterio
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd

# Define the raster (e.g. NDVI_Timeseries)
input_ras = r"C:\Users\VassarGIS\Downloads\drive-download-20230227T113702Z-001\TN_modis_daily_2023-02-02.tif"



# Define the raster for agriculture masking (e.g. bhuvan lulc)
mask_ras = "F:/TN_Modis_NDWI_250m/min_max/TN_AGRI_MASK_MODIS_250m_v2.tif"

mask_ras_arr = rasterio.open(mask_ras).read(1)

# Define the zones (e.g. polygons)
zones = "F:/TN_Modis_NDVI_250m/min_max/all_shapefiles_(except_state)/TNWRIMS_village_09112022_2315PM.shp"

out_csv_path = 'F:/TN_Modis_NDWI_250m/min_max/20230202.csv'

date_list = list(range(1,365,16))

# Create an empty DataFrame to store the statistics
zone = gpd.read_file(zones)

if zone.crs is None:
    zone = zone.set_crs(default_crs)

# Transform to a difference CRS.


# Open the raster dataset
with rasterio.open(input_ras) as src:
    # Get the number of bands in the dataset
    num_bands = src.count
    print(num_bands)
    zone = zone.to_crs(src.crs)
    affine = src.transform
    # Loop through each band
    for i in range(1, num_bands+1):
        # Get the band data as a numpy array
        band_raw = src.read(i)
        band = band_raw * mask_ras_arr
        
        # Calculate zonal statistics for the current band
        band_stats = zonal_stats(zone, band, stats='mean', affine=affine , nodata = 0)
        # Add the statistics to the DataFrame as a new column
        zone[date_list[i-1]] = [stat['mean'] for stat in band_stats]
        zone[date_list[i-1]] = zone[date_list[i-1]]/10000

    src.close()

zone.drop('geometry', axis=1, inplace= True)


zone = pd.DataFrame(zone)
zone.to_csv(out_csv_path)

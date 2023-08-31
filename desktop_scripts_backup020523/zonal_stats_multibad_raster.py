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

date_list = [1648080000000,1648512000000,1648944000000,1649376000000,1649808000000,1650240000000,1650672000000,1651104000000,1651536000000,1651968000000,1652400000000,1652832000000,1653264000000,1653696000000,1654128000000,1654560000000,1654992000000,1655424000000,1655856000000,1656288000000,1656720000000,1657152000000,1657584000000,1658016000000,1658448000000,1658880000000,1659312000000,1659744000000,1660176000000,1660608000000,1661040000000,1661472000000,1661904000000,1662336000000,1662768000000,1663200000000,1663632000000,1664064000000,1664496000000,1664928000000,1665360000000,1665792000000,1666224000000,1666656000000,1667088000000,1667520000000,1667952000000,1668384000000,1668816000000,1669248000000,1669680000000,1670112000000,1670544000000,1670976000000,1671408000000,1671840000000,1672272000000,1672704000000,1673136000000,1673568000000,1674000000000,1674432000000,1674864000000,1675296000000,1675728000000,1676160000000]

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

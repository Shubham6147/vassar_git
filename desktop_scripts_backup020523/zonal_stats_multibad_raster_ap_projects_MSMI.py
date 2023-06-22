import rasterio
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd
from datetime import datetime

date_list = [1648080000000,1648512000000,1648944000000,1649376000000,1649808000000,1650240000000,1650672000000,1651104000000,1651536000000,1651968000000,1652400000000,1652832000000,1653264000000,1653696000000,1654128000000,1654560000000,1654992000000,1655424000000,1655856000000,1656288000000,1656720000000,1657152000000,1657584000000,1658016000000,1658448000000,1658880000000,1659312000000,1659744000000,1660176000000,1660608000000,1661040000000,1661472000000,1661904000000,1662336000000,1662768000000,1663200000000,1663632000000,1664064000000,1664496000000,1664928000000,1665360000000,1665792000000,1666224000000,1666656000000,1667088000000,1667520000000,1667952000000,1668384000000,1668816000000,1669248000000,1669680000000,1670112000000,1670544000000,1670976000000,1671408000000,1671840000000,1672272000000,1672704000000,1673136000000,1673568000000,1674000000000,1674432000000,1674864000000,1675296000000,1675728000000,1676160000000]

all_projects = ['Bramhanapalli_uuid_update',  'Buduru_uuid_update',  'Chamalagudur_uuid_update',  'E_THANDRAPADU_uuid_update',  'KULLUR_uuid_update',  'MALYALA_I_uuid_update',  'MALYALA_II_uuid_update',  'MARLAMADIKI_III_uuid_update',  'MITTA_SOMAPURAM_uuid_update',  'MUDDUTAMAGI_uuid_update',  'SIVAPURAM_uuid_update',  'vallampadu_uuid_update']

ap_projects_file = r"C:\Users\VassarGIS\Downloads\AP_farms_merged\AP_farms_merged.shp"
ap_projects = gpd.read_file(ap_projects_file)



for project in all_projects:
    print(project)
    # Define the zones (e.g. polygons)
    zone = ap_projects[ap_projects['layer'] == project ]
    ##zone['NDVI'] = ''

    out_csv_path = 'F:/CROP_STRESS_AP_PROJECTS/NDMI_AP_PROJECTS/' + project + '_zonal.csv'
    # Define the raster (e.g. NDVI_Timeseries)
    input_ras = 'F:/CROP_STRESS_AP_PROJECTS/NDMI_AP_PROJECTS/' + project + '_NDMI_smooth.tif'


    if zone.crs is None:
        zone = zone.set_crs(default_crs)

    # Transform to a difference CRS.

    all_dates = []
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
            band = src.read(i)

            # Calculate zonal statistics for the current band
            band_stats = zonal_stats(zone, band, stats='mean', affine=affine)
            # Add the statistics to the DataFrame as a new column
            zone['NDMI'] = [stat['mean'] for stat in band_stats]
            #print(date_list[i-1])
            data_date = str(datetime.fromtimestamp(date_list[i-1]/1000.0).date())

            #print(data_date)
            zone['Date'] = data_date
            zone_1 = zone.copy()
            all_dates.append(zone_1)
        src.close()

    print('done with zonal stats')

    all_project_data = pd.concat(all_dates, axis = 0)
    all_project_data['NDMI'] = all_project_data['NDMI']/10000
    all_project_data.drop('geometry', axis=1, inplace= True)
    all_project_data = pd.DataFrame(all_project_data)

    all_project_data.to_csv(out_csv_path)

import rasterio
import pandas as pd
from rasterstats import zonal_stats
import geopandas as gpd
from datetime import datetime



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

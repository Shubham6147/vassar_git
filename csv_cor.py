
import pandas as pd
import glob

for csv_path in glob.glob("G:/Haryana/District/*.csv"):

    #csv_path = r"C:\Users\shubh\Downloads\NDMI_HR_district_2021-22_PANIPAT.csv"

    date_df = pd.read_csv(csv_path)

    date_df['system:time_start'] = pd.to_datetime(date_df['system:time_start'], unit='ms')

    date_df = date_df [ ['system:index', 'system:band_names', 'system:time_start']]

    date_df.to_csv(csv_path, index=False)
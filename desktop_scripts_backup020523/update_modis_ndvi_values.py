import os
import pandas as pd

# specify the folder containing the CSV files
folder = "F:/TN_Modis_NDVI_250m/min_max/updated"
save_folder = "F:/TN_Modis_NDVI_250m/min_max/updated"

# get a list of all CSV files in the folder
csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]

# loop through the CSV files
for file in csv_files:
    # read the CSV file
    df = pd.read_csv(os.path.join(folder, file), skipinitialspace = True)
    # get the last 23 columns
    df['Village'] = df['Village'].str.strip()
    #last_cols = df.columns[-23:]
    # multiply the last 23 columns by 0.001
    #df[last_cols] = df[last_cols] * 0.0001
    # save the modified CSV file to the save folder
    df.to_csv(os.path.join(save_folder, file), index=False)

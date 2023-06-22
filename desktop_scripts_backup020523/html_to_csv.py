import pandas as pd
import os
import glob

# list of XLSX file names
xlsx_files = glob.glob('C:/Users/VassarGIS/Downloads/Livestock_Odisha_Blocklevel/*.xls')

# create an empty dataframe to store the data
df_final = pd.DataFrame()

# loop through the XLSX files
for file in xlsx_files:
    df2 = pd.DataFrame()
    # read the XLSX file
    df = pd.read_html(file)[0]
    # drop first 4 rows
    #df = df.drop(df.index[''])
    # drop last row
    #df = df.drop(df.index[-1])
    # Add filename column to the dataframe
    df["filename"] = os.path.basename(file).split('.')[0]
    #for i in df:
        #df2[i[0]] = df[i]
    # append the data from the current file to the final dataframe
    df_final = df_final.append(df, ignore_index=True)
    

print(df_final)

df_final.to_csv('C:/Users/VassarGIS/Downloads/Livestock_Odisha_Blocklevel/merged_Livestock_Odisha_Blocklevel.csv')

import os
import pandas as pd

os.chdir("D:/Tamilnadu_KTCC_water_10days_max")

df = pd.read_csv(r"D:\Tamilnadu_KTCC_water_10days_max\download_links.csv")

for index, row in df.iterrows():
    #print(row["Links"])
    command = f'wget "{row["Links"]}"'
    print(command)
    os.system(command)
    break

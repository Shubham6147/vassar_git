
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import glob
import os

from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_timeframe(startDate, endDate, dates):

	cur_date = datetime.strptime(startDate, '%Y%m%d').date()
	end = datetime.strptime(endDate, '%Y%m%d').date()

	ref_list = []

	while cur_date <= end:
		month_temp = cur_date.month
		month = f"{month_temp:02}"
		ref_list.append(str(cur_date.year)+month)
		cur_date += relativedelta(months=1)

	year_1_dates = []
	for date in dates:
		if date[:6] in ref_list:
			year_1_dates.append(date)
	return year_1_dates


for wertness_csv in glob.glob("F:/TN_6vill/wetness/*_Apr14_uuid_S1_wetnwss.csv"):

    optram_output = wertness_csv[:-4] + 'sesonal.csv'
    vill_name = os.path.basename(wertness_csv).split('_')[0]
    print(vill_name)
    df_ndvi = pd.read_csv(wertness_csv)


    NDVI_filter_col = [col for col in df_ndvi if col.startswith('WET')]
    df_3 = pd.DataFrame()

    df_3['field_uuid'] = df_ndvi['field_uuid']


    for vi_name in NDVI_filter_col:
        
        optram_name = '20' + vi_name[4:]

        df_3[optram_name] = df_ndvi[vi_name].values    
    
    #df_3.to_csv(optram_output)

    dates = []
    columns = df_3.columns
    for col in columns:
        if col.startswith('2'):
            dates.append(col)
    
    start_list = ['20170401', '20171001', '20180401', '20181001','20190401', '20191001','20200401', '20201001','20210401', '20211001','20220401', '20221001',]
    end_list = ['20170930', '20180331', '20180930', '20190331', '20190930', '20200331', '20200930', '20210331', '20210930', '20220331', '20220930', '20230331',]
    years = ['2017-18_K', '2017-18_R','2018-19_K', '2018-19_R', '2019-20_K', '2019-20_R', '2020-21_K', '2020-21_R', '2021-22_K','2021-22_R', '2022-23_K', '2022-23_R']
    new_df = pd.DataFrame()
    new_df['field_uuid'] = df_3['field_uuid']
    for k in range(len(start_list)):
        year_1_dates = get_timeframe(start_list[k], end_list[k], dates)
        year_1 = ['field_uuid'] + year_1_dates
        curr_df = df_3[year_1]
        mean_list = []

        for i in range(len(curr_df)):
            arr = curr_df.iloc[i][1:].to_list()
            mean_list.append(np.mean(arr))
        
        new_df[years[k]] = mean_list
    new_df.to_csv(optram_output)
    #break  

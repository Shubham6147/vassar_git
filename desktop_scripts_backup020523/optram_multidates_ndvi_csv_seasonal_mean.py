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




def compute_optram(ndvi, swir):

    STR1  = ((1.0 - swir)**2.0)/(2.0 * swir)

    #------- Thresholds derived from STR and NDVI values 

    #DbS = 0.2 #Dry bare soil or intercept of dry edge
    #WsV = 0.34 #Water stressed vegetation

    #SbS = 1.76 #Saturated bare soil or intercept of wet edge
    #WwV = 2.53 #Well-watered vegetation

    ##The results were oversaturated so we have  changed the above thresholds
    
    DbS = 0 #Dry bare soil or intercept of dry edge
    WsV = 0.3 #Water stressed vegetation

    SbS = 2.2 #Saturated bare soil or intercept of wet edge
    WwV = 2.8 #Well-watered vegetation

    Sd = WsV - DbS #slope of dry edge
    Sw = WwV - SbS #Slope of Wet edge

    STRdry = (DbS + (Sd * ndvi))
    STRwet = (SbS + (Sw * ndvi))


    #OPTRAM  = ((STRwet - STR1)/(STRwet - STRdry))*100
    OPTRAM  = ((STRdry - STR1)/(STRdry - STRwet))*100


    #OPTRAM = OPTRAM.replace([np.inf, -np.inf], 0) 
    OPTRAM[OPTRAM > 100] = 100
    OPTRAM[OPTRAM < 0] = 0

    return OPTRAM    


for ndvi_csv in glob.glob('F:/TN_6vill/cor_data/*_NDVI_med_noise_cor.csv'):
    vill_name = os.path.basename(ndvi_csv).split('_')[0]
    print(vill_name)
    swir_csv = ndvi_csv[:-23] + '_SWIR_med_expand_mvng_avg_noise_cor.csv'
    optram_output = ndvi_csv[:-23] + '_OPTRAM_season_mean.csv'


    #ndvi_csv = 'F:/TN_6vill/cor_data/ADIYUR_Village_field_poly_uuid_Mapped_4326_polygon_NDVI_med_noise_cor.csv'

    df_ndvi = pd.read_csv(ndvi_csv)
    df_swir = pd.read_csv(swir_csv)

    NDVI_filter_col = [col for col in df_ndvi if col.startswith('VI')]
    df_3 = pd.DataFrame()

    df_3['Field_UUID'] = df_ndvi['Field_UUID']


    for vi_name in NDVI_filter_col:
        b11_name = 'B11' + vi_name[2:]
        optram_name = '20' + vi_name[3:]


        
        df_2 = pd.DataFrame()
        df_2['ndvi_vals'] = df_ndvi[vi_name].values
        df_2['swir_vals'] = df_swir[b11_name].values

        


        if df_2['swir_vals'].min() < 0:
            print(vill_name, b11_name)
            continue
        df_3[optram_name] = compute_optram(df_2['ndvi_vals'], df_2['swir_vals'])    
    
    #df_3.to_csv(optram_output_2)

    dates = []
    columns = df_3.columns
    for col in columns:
        if col.startswith('2'):
            dates.append(col)
    
    start_list = ['20170401', '20171001', '20180401', '20181001','20190401', '20191001','20200401', '20201001','20210401', '20211001','20220401', '20221001',]
    end_list = ['20170930', '20180331', '20180930', '20190331', '20190930', '20200331', '20200930', '20210331', '20210930', '20220331', '20220930', '20230331',]
    years = ['2017-18_1', '2017-18_2','2018-19_1', '2018-19_2', '2019-20_1', '2019-20_2', '2020-21_1', '2020-21_2', '2021-22_1','2021-22_2', '2022-23_1', '2022-23_2']
    new_df = pd.DataFrame()
    new_df['Field_UUID'] = df_3['Field_UUID']
    for k in range(len(start_list)):
        year_1_dates = get_timeframe(start_list[k], end_list[k], dates)
        year_1 = ['Field_UUID'] + year_1_dates
        curr_df = df_3[year_1]
        mean_list = []

        for i in range(len(curr_df)):
            arr = curr_df.iloc[i][1:].to_list()
            mean_list.append(np.mean(arr))
        
        new_df[years[k]] = mean_list
    new_df.to_csv(optram_output)
    #break  

        
#b7c65093-ba12-42d8-82e5-65bf48536a82     
#19bafdfc-5241-459c-8b07-7be9ed5ca336



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


    OPTRAM = OPTRAM.replace([np.inf, -np.inf], 0) 
    OPTRAM[OPTRAM > 100] = 100
    OPTRAM[OPTRAM < 0] = 0

    return OPTRAM
    
def compute_optram_swir(NDVI, STR):

    vd_opt = 0.3143
    vw_opt = 0.083
    id_opt = 0.5711
    iw_opt = 0.0406


    sd_opt = vd_opt - id_opt

    sw_opt = vw_opt - iw_opt


    STRdry = (id_opt + (sd_opt * NDVI))
    STRwet = (iw_opt + (sw_opt * NDVI))

    OPTRAM  = (STRdry - STR)/(STRdry - STRwet)*100
    return OPTRAM


for ndvi_csv in glob.glob('F:/TN_6vill/cor_data/*Updated_Apr14_NDVI_med_noise_cor.csv'):
    vill_name = os.path.basename(ndvi_csv).split('_')[0]
    print(vill_name)
    swir_csv = ndvi_csv[:-23] + '_SWIR_med_expand_mvng_avg_noise_cor.csv'
    optram_output_2 = ndvi_csv[:-23] + '_OPTRAM_season_mean.csv'
    optram_output = ndvi_csv[:-23] + '_OPTRAM.csv'

    #ndvi_csv = 'F:/TN_6vill/cor_data/ADIYUR_Village_field_poly_uuid_Mapped_4326_polygon_NDVI_med_noise_cor.csv'

    df_ndvi = pd.read_csv(ndvi_csv)
    df_swir = pd.read_csv(swir_csv)

    NDVI_filter_col = [col for col in df_ndvi if col.startswith('VI')]
    df_3 = pd.DataFrame()
    df_4 = pd.DataFrame()

    df_3['field_uuid'] = df_ndvi['field_uuid']
    df_4['field_uuid'] = df_ndvi['field_uuid']
    
    for vi_name in NDVI_filter_col:
        b11_name = 'B11' + vi_name[2:]
        optram_name = '20' + vi_name[3:]


        
        df_2 = pd.DataFrame()
        df_2['ndvi_vals'] = df_ndvi[vi_name].values
        df_2['swir_vals'] = df_swir[b11_name].values

        

        df_4[optram_name] = compute_optram(df_2['ndvi_vals']/10000, df_2['swir_vals']/10000)

        if df_2['swir_vals'].min() < 0:
            print(vill_name, b11_name)
            continue
        df_3[optram_name] = compute_optram(df_2['ndvi_vals']/10000, df_2['swir_vals']/10000)    

    df_4.to_csv(optram_output)

    #df_3.to_csv(optram_output_2)

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
    new_df.to_csv(optram_output_2)
    #break  
        

        
        



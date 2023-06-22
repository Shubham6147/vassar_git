import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde
import glob
import os


df_final = pd.DataFrame()

df_final['ndvi_vals'] = ''
df_final['swir_vals'] = ''
df_final['vill'] = ''
df_final['col_name'] = '' 

for ndvi_csv in glob.glob('F:/TN_6vill/cor_data/*_NDVI_med_noise_cor.csv'):
    vill_name = os.path.basename(ndvi_csv).split('_')[0]
    print(vill_name)
    swir_csv = ndvi_csv[:-23] + '_SWIR_med_expand_mvng_avg_noise_cor.csv'
    #ndvi_csv = 'F:/TN_6vill/cor_data/ADIYUR_Village_field_poly_uuid_Mapped_4326_polygon_NDVI_med_noise_cor.csv'

    df_ndvi = pd.read_csv(ndvi_csv)
    df_swir = pd.read_csv(swir_csv)

    NDVI_filter_col = [col for col in df_ndvi if col.startswith('VI')]

    for vi_name in NDVI_filter_col:
        b11_name = 'B11' + vi_name[2:]
        df_2 = pd.DataFrame()
        
        df_2['ndvi_vals'] = df_ndvi[vi_name].values
        df_2['swir_vals'] = df_swir[b11_name].values

        if df_2['swir_vals'].min() < 0:
            print(vill_name, b11_name)
            continue
            
        df_2['vill'] = str(vill_name)
        df_2['col_name'] = str(b11_name)

        df_final = df_final.append(df_2, ignore_index = True)
        
df_final = df_final[df_final['swir_vals'] > 0]

df_final['ndvi_vals'] = df_final['ndvi_vals']/10000
df_final['swir_vals'] = df_final['swir_vals']/10000

df_final['str_vals'] = ((1.0 - df_final['swir_vals'])**2.0)/(2.0 * df_final['swir_vals'])

df_3 = pd.DataFrame()
final_ndvi = []
final_swir = []


interval_param = 0.02
itr = int(1 / interval_param)

for i in range(0, itr ):
    floting_val = (i +1)  * interval_param
    print(floting_val , floting_val - interval_param)
    min_val = floting_val - interval_param
    df_filterd = df_final[(df_final['ndvi_vals'] < floting_val) &  (df_final['ndvi_vals'] > min_val)]

    swir_max = df_filterd.str_vals.quantile(0.95)
    swir_min = df_filterd.str_vals.quantile(0.02)

    final_ndvi.append(min_val)
    final_ndvi.append(min_val)

    final_swir.append(swir_max)
    final_swir.append(swir_min)

    df_filterd_swir = df_filterd[(df_filterd['str_vals'] < swir_max) &  (df_filterd['str_vals'] > swir_min)]
    df_3 = df_3.append(df_filterd_swir)


#df_3 = pd.DataFrame({'ndvi_vals': final_ndvi , 'swir_vals': final_swir})





#df_final = df_final[df_final['swir_vals'] > df_final['swir_vals'].quantile(0.05)]
#df_final = df_final[df_final['swir_vals'] < df_final['swir_vals'].quantile(0.9)]

#df_3 = df_final.copy()

#plt.scatter(df_final['ndvi_vals'].values, df_final['swir_vals'].values , c='blue')
#plt.show()

#plt.scatter(df_3['ndvi_vals'].values, df_3['swir_vals'].values , c='blue')
#plt.show()



# Calculate the point density
#xy = np.vstack([df_3['ndvi_vals'].values,df_3['swir_vals'].values])
#z = gaussian_kde(xy)(xy)

#plt.scatter(x='ndvi_vals', y='swir_vals', data=df_3, c=z, vmin=0, vmax=100)

plt.show()


#----------scaled

#df_3['str_vals'] = ((1.0 - df_3['swir_vals'])**2.0)/(2.0 * df_3['swir_vals'])

df_scaled = (df_3[['ndvi_vals', 'str_vals']] - df_3[['ndvi_vals', 'str_vals']].quantile(0.05))/ (df_3[['ndvi_vals', 'str_vals']].quantile(0.95) - df_3[['ndvi_vals', 'str_vals']].quantile(0.05))

#plt.scatter(x='ndvi_vals', y='swir_vals', data=df, c='GR', vmin=0, vmax=100)

#plt.show()



import mpl_scatter_density # adds projection='scatter_density'
from matplotlib.colors import LinearSegmentedColormap

# "Viridis-like" colormap with white background
white_viridis = LinearSegmentedColormap.from_list('white_viridis', [
    (0, '#ffffff'),
    (1e-20, '#440053'),
    (0.2, '#404388'),
    (0.4, '#2a788e'),
    (0.6, '#21a784'),
    (0.8, '#78d151'),
    (1, '#fde624'),
], N=256)

def using_mpl_scatter_density(fig, x, y):
    ax = fig.add_subplot(1, 1, 1, projection='scatter_density')#, xlim = (-1, 1), ylim = (-1,1))
    density = ax.scatter_density(x, y, cmap=white_viridis)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 3])
    fig.colorbar(density, label='Number of points per pixel')

#fig = plt.figure()
#using_mpl_scatter_density(fig, df_3['ndvi_vals'].values, df_3['swir_vals'].values )
#plt.show()

#plt.clf()

fig = plt.figure()
using_mpl_scatter_density(fig, df_3['ndvi_vals'], df_3['str_vals'] )
#using_mpl_scatter_density(fig, df_3['ndvi_vals'].values/10000, df_3['swir_vals'].values/10000 )
plt.show()

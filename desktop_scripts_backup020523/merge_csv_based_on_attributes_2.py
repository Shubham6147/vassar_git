import pandas as pd

df1 = pd.read_excel('/home/vassar/Downloads/BBSR_commercial_demand.xlsx')
df2 = pd.read_csv('/home/vassar/Downloads/Book1.csv')
#a = zip(df2['Block'],df2['Block_new'])
#a = dict(a)

#df1['Block_new'] = df1['Block'].map(a)
df = pd.merge(df1, df2, on='Ward Number', how='left')
df.to_csv('/home/vassar/Downloads/BBSR_commercial_demand_merged.csv')

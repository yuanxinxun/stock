#20210624更新读取数据的效率和通用性，生成了相关性系数矩阵
import os
import sys
import numpy as np
import pandas as pd
import csv
import stock_basic

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', 10)
pd.set_option('display.width',1000)

industry_code_namedf=stock_basic.get_code_namedf(stock_basic.INDASTRY)
Index_code='399006.SZ'

#获取数据字典，key为代码，值为日期序列df
industry_dict=stock_basic.get_datadict(industry_code_namedf.index,'D:\python_project\source_data\industrydata',usecols=[0,2],columns=['close'],header=0)#带header等于0保证数据格式为float
Index_df=pd.read_csv('D:\python_project\\source_data\\Indexdata\\399006.SZ.csv',parse_dates=[0],index_col=0,usecols=[0,2],header=0)
for key in industry_dict.keys():#设置列名为行业代码
    industry_dict[key].columns=[key]
close_df=pd.concat([industry_dict[key] for key in industry_dict.keys()],axis=1)
close_df[Index_code]=Index_df['CLOSE'][(Index_df.index>=min(close_df.index))&(Index_df.index<=max(close_df.index))].values
corr_df=close_df.corr()
corr_df_near=close_df[-30:].corr()
close_df_T=close_df.T
increase_rank_far=(close_df_T.iloc[:,-1]/close_df_T.iloc[:,-91]).rank(ascending=False)#涨幅排名
increase_rank_mid=(close_df_T.iloc[:,-1]/close_df_T.iloc[:,-31]).rank(ascending=False)
increase_rank_near=(close_df_T.iloc[:,-1]/close_df_T.iloc[:,-6]).rank(ascending=False)

Index_corr_df=corr_df.loc[:,[Index_code]]
Index_corr_df['corr_df_near']=corr_df_near[Index_code]
Index_corr_df['difference_abs']=abs(Index_corr_df['corr_df_near']-Index_corr_df[Index_code])
Index_corr_df['name']=[(industry_code_namedf.loc[code].values[0] if code in industry_code_namedf.index else code) for code in Index_corr_df.index]
Index_corr_df['IRfar']=increase_rank_far
Index_corr_df['IRmid']=increase_rank_mid
Index_corr_df['IRnear']=increase_rank_near
sort_df_bydiff=Index_corr_df.sort_values(by='difference_abs',ascending=False)
sort_df_bynear=Index_corr_df.sort_values(by='IRnear')
print(sort_df_bydiff)


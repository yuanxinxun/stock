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

code_namedict={}
code_namelist = csv.reader(open('D:\python_project\source_data\code_name\industrycode_name_list.csv','r'))#类似文件指针，只能循环一次
for data in code_namelist:
    if len(data)>=2:
        code=data[0]
        code_namedict[code]=data[1]

#获取数据字典，key为代码，值为日期序列df
industry_dict=stock_basic.get_datadict(code_namedict.keys(),'D:\python_project\source_data\industrydata',usecols=[0,2],columns=['close'])
Index_df=pd.read_csv('D:\python_project\\source_data\\Indexdata\\399006.SZ.csv',parse_dates=[0],index_col=0,usecols=[0,2],header=None)
for key in industry_dict.keys():#设置列名为行业代码
    industry_dict[key].columns=[key]
close_df=pd.concat([industry_dict[key] for key in industry_dict.keys()],axis=1)
close_df['399006.SZ']=Index_df[2][(Index_df.index>=min(close_df.index))&(Index_df.index<=max(close_df.index))].values
corr_df=close_df.corr()
corr_df_60=close_df[-60:].corr()

Index_corr_df=corr_df.loc[:,['399006.SZ']]
Index_corr_df['Index_60']=corr_df_60['399006.SZ']
Index_corr_df['difference']=Index_corr_df['Index_60']-Index_corr_df['399006.SZ']
Index_corr_df['difference_abs']=abs(Index_corr_df['difference'])
Index_corr_df['name']=[(code_namedict[code] if code in code_namedict.keys() else code) for code in Index_corr_df.index]
sort_df_bydiff=Index_corr_df.sort_values(by='difference',ascending=False)
sort_df_byindex=Index_corr_df.sort_values(by='399006.SZ',ascending=False)
sort_df_byIndex60=Index_corr_df.sort_values(by='Index_60',ascending=False)
#utf-8
import sys
import numpy as np
import pandas as pd
import csv
import stock_basic

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log

datalen=260
ma_num=20
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

industry_code_namedf=stock_basic.get_code_namedf(stock_basic.INDASTRY)
stock_code_namedf=stock_basic.get_code_namedf(stock_basic.STOCK)
#获取数据字典，key为代码，值为日期序列df
stock_dict=stock_basic.get_datadict(stock_code_namedf.index,'D:\python_project\source_data\data',header=0,userows=datalen,usecols=[0,1,2])
stock_ma_dict={}

for key in stock_dict.keys():
    if stock_dict[key]['AMT'][-1]<100000000:
        continue
    i=0
    close_data=stock_dict[key]['CLOSE']
    ma=close_data.rolling(ma_num,min_periods=1).mean()
    if ma[-1]>ma[-2]:        
        i=i+1
    if min(ma[-5:])==min(ma[-30:]):
        i=i+1
    if i==2:
        print(key,stock_code_namedf.loc[key]['SEC_NAME'])

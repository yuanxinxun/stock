#20210624更新读取数据的效率和通用性，生成了相关性系数矩阵
import datetime
import time
import csv
import os
import logging
import numpy as np
import pandas as pd
import stock_basic

def get_result_by_threshold(datadict,column_name,threshold):
    list_by_threshold=[]
    amt=0
    for key in datadict.keys():
        try:
            df=datadict[key]
            if df[column_name].mean()>threshold:
                list_by_threshold.append(key)
                amt+=df[column_name].mean()
        except Exception as e:
            log(str(e))
    return list_by_threshold

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log
#日期字符串格式统一为20200202
today=datetime.datetime.now().strftime('%Y%m%d')
#获得股票代码-名称列表
code_namedict={}
code_activelist=[]
code_namelist = csv.reader(open('D:\python_project\source_data\code_name\code_name_list.csv','r',encoding='utf-8'))#类似文件指针，只能循环一次
for data in code_namelist:
    if len(data)>2:
        code=data[0]
        code_namedict[code]=data[1]
#读取每天的数据，汇总到字典里
#收到的数据里有nan
#0股票代码1成交量2收盘价3涨跌幅4市值
stockdict=stock_basic.get_datadict(code_namedict.keys(),'D:\python_project\source_data\data',usecols=[0,2]);
for key in stockdict.keys():
    stockdict[key].columns=[code_namedict[key]]
close_df=pd.concat([stockdict[key] for key in stockdict.keys()],axis=1)
corr_df=close_df.corr()

#pandas设置最大显示行和列
pd.set_option('display.max_rows', 100,'display.max_columns', 10,"display.min_rows",30,'display.width',1000)

os.chdir(maincwd)
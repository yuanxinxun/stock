#utf-8
#20210624更新读取数据的效率和通用性，生成了相关性系数矩阵
import os
import sys
from scipy import stats
from WindPy import w
import numpy as np
import pandas as pd
import csv
import stock_basic
import matplotlib.pyplot as plt

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log

datalen=300
amt_threshold=10000*10000*1#平均成交量的最小值，去除成交量非常小的板块
ma_num=20
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

industry_code_namedf=stock_basic.get_code_namedf(stock_basic.INDASTRY)
stock_code_namedf=stock_basic.get_code_namedf(stock_basic.STOCK)
#获取数据字典，key为代码，值为日期序列df
industry_dict=stock_basic.get_datadict(industry_code_namedf.index,'D:\python_project\source_data\industrydata',header=0,userows=datalen,usecols=[0,1,2])
stock_dict=stock_basic.get_datadict(stock_code_namedf.index,'D:\python_project\source_data\data',header=0,userows=datalen,usecols=[0,2])
for key in industry_dict.keys():
    industry_dict[key].columns=['AMT',key]
industry_close_df=pd.concat([industry_dict[key][key] for key in industry_dict.keys()],axis=1)
for key in stock_dict.keys():
    stock_dict[key].columns=[key]#设置列名为股票代码
stock_close_df=pd.concat([stock_dict[key] for key in stock_dict.keys()],axis=1)

ma_result_list=[]
for key in list(industry_dict.keys()):#迭代中改了字典，所以要加list
    if industry_dict[key]['AMT'].mean()<amt_threshold:
        continue
    industry_info=industry_code_namedf.loc[key]
    i=0
    close_data=industry_dict[key][key]
    ma=close_data.rolling(ma_num,min_periods=1).mean()
    if ma[-1]>ma[-2]:        
        i=i+10
    if min(ma[-5:])==min(ma[-30:]):
        i=i+1
    if abs(close_data[-1]-ma[-1])<close_data[-20:].std():
        i=i+2
    if i>10:
        ma_result_list.append(pd.Series([i,industry_info['SEC_NAME'],round(industry_dict[key]['AMT'][-1]/100000000,2),round(max(close_data[-10:])/min(close_data[-10:])-1,3)*100],name=key))
ma_result_df=pd.DataFrame(ma_result_list)
if len(ma_result_df)>0:
    ma_result_df.columns=['i','name','amt','amplitude']
ma_result_df=ma_result_df.groupby('i',sort=True).apply(lambda x:x.sort_values(by='amplitude',ascending=False))#降序


#用收盘价斜率筛选股票
w.start()
slope_df=pd.DataFrame(columns=["name","slope"])
is_notrun_slope=True#是否跑了斜率
print("输入r**计算**天长度的斜率")
print("输入6位数数字，查看指数成分")
print("输入整数或负数，显示前几行或最后几行结果")
print("输入q，退出")
while True:
    inputstr=input("Enter your input: ") 
    if len(inputstr)==0:inputstr='abcdefg'
    if inputstr=="q":
        break
    if is_notrun_slope or inputstr[0]=="r":
        is_notrun_slope=False
        slope_df=pd.DataFrame(columns=["name","slope"])
        i=10
        if inputstr[0]=="r":
            i=int(inputstr[1:])
        slope_df["slope"]=industry_close_df.apply(lambda y:stats.linregress(range(i),y[-i:]/y[-i])[0],axis=0).values
        slope_df.index=industry_close_df.columns
        slope_df["name"]=[industry_code_namedf.loc[code,"SEC_NAME"] for code in slope_df.index]
        slope_df=slope_df.sort_values(by=["slope"],ascending=False)
        stock_slope_df=stock_close_df.apply(lambda y:stats.linregress(range(i),y[-i:]/y[-i])[0],axis=0)
        stock_slope_df.name="slope"
    if inputstr[0]=="r":#为了is_notrun_slope=True的时候也能正常执行，保持程序丝滑
        pass
    elif len(inputstr)==6:
        industry_code="CI"+inputstr+".WI"
        errcode,winddf=w.wset("sectorconstituent",windcode=industry_code,usedf=True)
        if len(winddf)==0:
            log("结果小于0，请检查输入是否正确")
            continue
        #获取当前板块斜率排行
        print("%s:%d/%d"%(industry_code_namedf.loc[industry_code,'SEC_NAME'],slope_df.index.get_loc(industry_code)+1,len(slope_df)))
        winddf.set_index(["wind_code"], inplace=True)
        winddf=pd.concat([winddf,stock_slope_df],axis=1,join='inner')
        winddf=winddf.sort_values(by=["slope"],ascending=False)
        print(winddf)
        #在这里画斜率变化率的图
    elif inputstr.isnumeric() or inputstr[0]=="-":
        show_len=int(inputstr)
        print("平均斜率：%f"%slope_df["slope"].mean())
        if show_len>0:
            print(slope_df[:show_len])
        else:
            print(slope_df[show_len:])
    elif inputstr[0]=="c":
        inputstr=inputstr[1:]
        print(slope_df[slope_df['name'].str.contains(inputstr)])
    elif inputstr[0]=='d':
        inputstr=inputstr[1:]
        industry_code="CI"+inputstr+".WI"
        industry_close_df[industry_code].plot(kind='line')
        plt.show()
    elif inputstr[0]=="p":
        print(ma_result_df)
        print(len(ma_result_df))
    else:
        log("输入错误")
        print("输入r**计算**天长度的斜率")
        print("输入6位数数字，查看指数成分")
        print("输入整数或负数，显示前几行或最后几行结果")       
        print("C汉字，输出包含汉字的板块")
        print("输入q，退出")
os.chdir(maincwd)
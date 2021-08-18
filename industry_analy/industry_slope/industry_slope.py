#20210624更新读取数据的效率和通用性，生成了相关性系数矩阵
import os
import sys
from scipy import stats
from WindPy import w
import numpy as np
import pandas as pd
import csv
import stock_basic

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log

industry_code_namedict=stock_basic.get_code_namedict(stock_basic.INDASTRY)
stock_code_namedict=stock_basic.get_code_namedict(stock_basic.STOCK)
#获取数据字典，key为代码，值为日期序列df
industry_dict=stock_basic.get_datadict(industry_code_namedict.keys(),'D:\python_project\source_data\industrydata',userows=30,columns=['amt','close'])
stock_dict=stock_basic.get_datadict(stock_code_namedict.keys(),'D:\python_project\source_data\data',userows=30,usecols=[0,2])
for key in stock_dict.keys():
    stock_dict[key].columns=[key]#设置列名为行业代码
    stock_dict[key]=stock_dict[key]/stock_dict[key].iloc[0]#归一化
stock_close_df=pd.concat([stock_dict[key] for key in stock_dict.keys()],axis=1)
stock_close_df=stock_close_df.T

#用收盘价斜率筛选股票

w.start()
slope_df=pd.DataFrame(columns=["name","slope"])
use_trade_minamt=10000*10000*1#平均成交量的最小值，去除成交量非常小的板块
is_notrun_slope=True#是否跑了斜率
print("输入r**计算**天长度的斜率")
print("输入6位数数字，查看指数成分")
print("输入整数或负数，显示前几行或最后几行结果")
print("输入n，退出")
while True:
    inputstr=input("Enter your input: ") 
    if inputstr=="n":
        break
    if is_notrun_slope or inputstr[0]=="r":
        is_notrun_slope=False
        slope_df=pd.DataFrame(columns=["name","slope"])
        i=10
        if inputstr[0]=="r":
            i=int(inputstr[1:])
        for code,value_df in industry_dict.items():
            use_trade_startday=value_df.index[-i]#测试斜率的起始时间
            trade_daylen=len(value_df)
            amt_avr=value_df["amt"].mean()
            if amt_avr<use_trade_minamt:#滤掉平均成交量过低的板块
                log("忽略%s板块%s，平均成交额%.2f亿"%(code,industry_code_namedict[code],amt_avr/100000000))
                continue
            close_series=value_df["close"][value_df.index>=use_trade_startday]
            close=close_series/close_series[0]#归一化
            trade_daylen=len(close)
            slope=(np.polyfit(range(trade_daylen),close,deg=1))[0]
            slope_df.loc[code]=[industry_code_namedict[code],slope]
        stock_slope_df=stock_close_df.apply(lambda y:stats.linregress(range(i),y[-i:])[0],axis=1)
        stock_slope_df.name="slope"
        slope_df=slope_df.sort_values(by=["slope"],ascending=False)
    if inputstr[0]=="r":#为了is_notrun_slope=True的时候也能正常执行，保持程序丝滑
        pass
    elif len(inputstr)==6:
        errcode,winddf=w.wset("sectorconstituent",windcode=inputstr+".SI",usedf=True)
        winddf.set_index(["wind_code"], inplace=True)
        winddf=pd.concat([winddf,stock_slope_df],axis=1,join='inner')
        winddf=winddf.sort_values(by=["slope"],ascending=False)
        print(winddf)
    elif inputstr.isnumeric() or inputstr[0]=="-":
        i=int(inputstr)
        print("平均斜率：%f"%slope_df["slope"].mean())
        if i>0:
            print(slope_df[:i])
        else:
            print(slope_df[i:])
    else:
        log("输入错误")
        print("输入r**计算**天长度的斜率")
        print("输入6位数数字，查看指数成分")
        print("输入整数或负数，显示前几行或最后几行结果")
        print("输入n，退出")
os.chdir(maincwd)
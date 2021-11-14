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

datalen=90

industry_code_namedict=stock_basic.get_code_namedict(stock_basic.INDASTRY)
stock_code_namedict=stock_basic.get_code_namedict(stock_basic.STOCK)
#获取数据字典，key为代码，值为日期序列df
industry_dict=stock_basic.get_datadict(industry_code_namedict.keys(),'D:\python_project\source_data\industrydata',userows=datalen,columns=['amt','close'])
stock_dict=stock_basic.get_datadict(stock_code_namedict.keys(),'D:\python_project\source_data\data',userows=datalen,usecols=[0,2])
for key in industry_dict.keys():
    industry_dict[key].columns=[key+'amt',key]
industry_close_df=pd.concat([industry_dict[key][key] for key in industry_dict.keys()],axis=1)
for key in stock_dict.keys():
    stock_dict[key].columns=[key]#设置列名为股票代码
stock_close_df=pd.concat([stock_dict[key] for key in stock_dict.keys()],axis=1)

#用收盘价斜率筛选股票
w.start()
slope_df=pd.DataFrame(columns=["name","slope"])
use_trade_minamt=10000*10000*1#平均成交量的最小值，去除成交量非常小的板块
is_notrun_slope=True#是否跑了斜率
print("输入r**计算**天长度的斜率")
print("输入6位数数字，查看指数成分")
print("输入整数或负数，显示前几行或最后几行结果")
print("输入q，退出")
while True:
    inputstr=input("Enter your input: ") 
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
        slope_df["name"]=[industry_code_namedict[code[0:9]] for code in slope_df.index]
        slope_df=slope_df.sort_values(by=["slope"],ascending=False)
        stock_slope_df=stock_close_df.apply(lambda y:stats.linregress(range(i),y[-i:]/y[-i])[0],axis=0)
        stock_slope_df.name="slope"
    if inputstr[0]=="r":#为了is_notrun_slope=True的时候也能正常执行，保持程序丝滑
        pass
    elif len(inputstr)==6:
        industry_code=inputstr+".SI"
        errcode,winddf=w.wset("sectorconstituent",windcode=industry_code,usedf=True)
        if len(winddf)==0:
            log("结果小于0，请检查输入是否正确")
            continue
        #获取当前板块斜率排行
        print("%s:%d/%d"%(industry_code_namedict[industry_code],slope_df.index.get_loc(industry_code)+1,len(slope_df)))
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
    else:
        log("输入错误")
        print("输入r**计算**天长度的斜率")
        print("输入6位数数字，查看指数成分")
        print("输入整数或负数，显示前几行或最后几行结果")
        print("输入q，退出")
os.chdir(maincwd)
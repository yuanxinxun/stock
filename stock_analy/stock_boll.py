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
amt_threshold=1*100000000
trade_day_len=10
ma_num=20
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

industry_code_namedf=stock_basic.get_code_namedf(stock_basic.INDASTRY)
stock_code_namedf=stock_basic.get_code_namedf(stock_basic.STOCK)
#获取数据字典，key为代码，值为日期序列df
stock_dict=stock_basic.get_datadict(stock_code_namedf.index,'D:\python_project\source_data\data',header=0,userows=datalen,usecols=[0,1,2])
stock_ma_result_list=[]

for key in stock_dict.keys():
    if stock_dict[key]['AMT'][-1]<amt_threshold:
        continue
    i=0
    close_data=stock_dict[key]['CLOSE']
    ma=close_data.rolling(ma_num,min_periods=1).mean()
    if ma[-1]>ma[-2]:        
        i=i+1
    if min(ma[-5:])==min(ma[-30:]):
        i=i+1
    if i==2:
        stock_info=stock_code_namedf.loc[key]
        stock_ma_result_list.append(pd.Series([stock_info['SEC_NAME'],round(stock_info['AMT']/100000000,2),stock_info['VAL_PE_DEDUCTED_TTM'],stock_info['PROVINCE']],name=key))
ma_result_df=pd.DataFrame(stock_ma_result_list)
ma_result_df.columns=['name','amt','pe_ttm','province']
ma_result_df=ma_result_df.sort_values(by='amt',ascending=False)#降序

trade_day_increase_list=[]
for key in stock_dict.keys():
    if stock_dict[key]['AMT'][-1]<amt_threshold:
        continue
    close_data=stock_dict[key]['CLOSE']
    stock_increase=close_data[-1]/close_data[-trade_day_len-1]-1
    stock_info=stock_code_namedf.loc[key]
    trade_day_increase_list.append(pd.Series([stock_info['SEC_NAME'],stock_increase,round(stock_info['AMT']/100000000,2),stock_info['VAL_PE_DEDUCTED_TTM'],stock_info['PROVINCE']],name=key))

increase_result_df=pd.DataFrame(trade_day_increase_list)
increase_result_df.columns=['name','increase','amt','pe_ttm','province']
increase_result_df=increase_result_df.sort_values(by='increase',ascending=False)#降序
print("输入r**计算**天长度的斜率")
print("输入6位数数字，查看指数成分")
print("输入整数或负数，显示前几行或最后几行结果")
print("输入q，退出")
while True:
    inputstr=input("Enter your input: ") 
    if len(inputstr)==0:inputstr='abcdefg'
    if inputstr=="q":
        break
    if inputstr[0]=="r":
        trade_day_len=int(inputstr[1:])
        trade_day_increase_list=[]
        for key in stock_dict.keys():
            if stock_dict[key]['AMT'][-1]<amt_threshold:
                continue
            close_data=stock_dict[key]['CLOSE']
            stock_increase=close_data[-1]/close_data[-trade_day_len-1]-1
            stock_info=stock_code_namedf.loc[key]
            trade_day_increase_list.append(pd.Series([stock_info['SEC_NAME'],stock_increase,round(stock_info['AMT']/100000000,2),stock_info['VAL_PE_DEDUCTED_TTM'],stock_info['PROVINCE']],name=key))

        increase_result_df=pd.DataFrame(trade_day_increase_list)
        increase_result_df.columns=['name','increase','amt','pe_ttm','province']
        increase_result_df=increase_result_df.sort_values(by='increase',ascending=False)#降序
    elif len(inputstr)==6:
        increase_result_df[increase_result_df.index.str.contains(inputstr)]
    elif inputstr.isnumeric() or inputstr[0]=="-":
        show_len=int(inputstr)
        print("平均涨幅：%f%%"%(increase_result_df["increase"].mean()/100))
        if show_len>0:
            print(increase_result_df[:show_len])
        else:
            print(increase_result_df[show_len:])
    elif inputstr[0]=="C":
        inputstr=inputstr[1:]
        print(increase_result_df[increase_result_df['name'].str.contains(inputstr)])
    else:
        log("输入错误")
        print("输入r**计算**天长度的斜率")
        print("输入6位数数字，查看指数成分")
        print("输入整数或负数，显示前几行或最后几行结果")       
        print("C汉字，输出包含汉字的板块")
        print("输入q，退出")


os.chdir(maincwd)
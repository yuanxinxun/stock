#utf-8
import sys
import numpy as np
import pandas as pd
import csv
import stock_basic
import os

def get_stock_score(index_closes,stock_closes):
    score=0
    for i in range(len(index_closes)):
        index=index_closes[i]
        stock=stock_closes[i]
        if index<0:
            if stock>index:
                score+=3
                if stock>0:
                    score+=2
                if stock>5:
                    +1
            else:
                score-=1

        else:
            if (stock-index)>0:
                score+=1
            if (stock-index)>3:
                score+=2
            if (stock-index)<0:
                score-=2

    return score


maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log

datalen=100
amt_threshold=0.3*100000000#成交金额阈值
trade_day_len=10
ma_num=20
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 1000)

Index_df=pd.read_csv('D:\python_project\\source_data\\Indexdata\\000001.SH.csv',parse_dates=[0],index_col=0,usecols=[0,3],header=0)
industry_code_namedf=stock_basic.get_code_namedf(stock_basic.INDASTRY)
stock_code_namedf=stock_basic.get_code_namedf(stock_basic.STOCK)

#获取数据字典，key为代码，值为日期序列df
stock_dict=stock_basic.get_datadict(stock_code_namedf.index,'D:\python_project\source_data\data',header=0,userows=datalen,usecols=[0,1,2,3])

initial=True
print("输入r**计算**天长度的斜率")
print("输入l**计算重置成交额门槛为**亿")
print("输入6位数数字，查看指数成分")
print("输入整数或负数，显示前几行或最后几行结果")
print("输入q，退出")
while True:
    inputstr=input("Enter your input: ") 
    if len(inputstr)==0:inputstr='abcdefg'
    if inputstr=="q":
        break
    if inputstr[0]=="r" or initial==True:
        if inputstr[0]=="r":
            trade_day_len=int(inputstr[1:])
        initial=False       
        trade_day_increase_list=[]
        #amplitude 振幅
        for key in stock_dict.keys():
            stock_amt=stock_dict[key]['AMT'][-trade_day_len:]
            if stock_amt.mean()<amt_threshold or stock_amt.duplicated().sum()>0:
                continue
            close_data=stock_dict[key]['CLOSE']
            stock_increase=close_data[-1]/close_data[-trade_day_len-1]-1
            Index_pct_data=Index_df['PCT_CHG'][-trade_day_len:]
            stock_pct_data=stock_dict[key]['PCT_CHG'][-trade_day_len:]
            stock_score=get_stock_score(Index_pct_data,stock_pct_data)
            stock_info=stock_code_namedf.loc[key]
            trade_day_increase_list.append(pd.Series([stock_info['SEC_NAME'],stock_score,stock_increase,round(stock_info['AMT']/100000000,2),round(max(close_data[-trade_day_len-1:])/min(close_data[-trade_day_len-1:])-1,3)*100,stock_info['PROVINCE'],stock_info['INDUSTRY_CITIC']],name=key))

        increase_result_df=pd.DataFrame(trade_day_increase_list)
        increase_result_df.columns=['name','score','increase','amt','amplitude','province','industry']
        increase_result_df=increase_result_df.sort_values(by='score',ascending=False)#降序
        print("结果总数：%d"%(len(increase_result_df)))
    if inputstr[0]=="r":
        pass
    elif inputstr.isnumeric() or inputstr[0]=="-":
        show_len=int(inputstr)
        if show_len>0:
            print(increase_result_df[:show_len])
        else:
            print(increase_result_df[show_len:])
        print("平均涨幅：%f%%"%(increase_result_df["increase"].mean()*100))
    elif inputstr[0]=="c":
        inputstr=inputstr[1:]
        print(increase_result_df[increase_result_df['name'].str.contains(inputstr)])
    elif inputstr[0]=="p":
        print(ma_result_df)
        print(len(ma_result_df))
    elif inputstr[0]=="l":
        amt_threshold=float(inputstr[1:])*100000000
        print(amt_threshold)
    elif inputstr[0]=='g':
        show_len=int(inputstr[1:])
        increase_result_df['industry'][:show_len].value_counts()
    elif inputstr[0]=='t':
        begin_day=Index_df.index[-trade_day_len]
        print("数据长度：%d,起始日期：%s"%(trade_day_len,begin_day))
    elif len(inputstr)==6:
        increase_result_df[increase_result_df.index.str.contains(inputstr)]
    else:
        log("输入错误")
        print("输入r**计算**天长度的斜率")
        print("输入l**计算重置成交额门槛为**亿")
        print("输入g**计算前**行分组情况")
        print('输入t，显示目前天数，起始日期')
        print("输入6位数数字，查看指数成分")
        print("输入整数或负数，显示前几行或最后几行结果")       
        print("C汉字，输出包含汉字的板块")
        print("输入q，退出")


os.chdir(maincwd)
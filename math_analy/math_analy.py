#20211106创建
import os
import sys
from scipy import stats
import numpy as np
import pandas as pd
import csv
import stock_basic

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
log=stock_basic.log

datalen=999
industry_data_ready=False
stock_data_ready=False
industry_code_namedict=stock_basic.get_code_namedict(stock_basic.INDASTRY)
stock_code_namedict=stock_basic.get_code_namedict(stock_basic.STOCK)
while True:
    print('Enter the corr property')
    target_code=input('Enter code: ') 
    begin_day=input('Enter begin_day: ') 
    end_day=input('Enter end_day: ') 
    scope=input('Enter scope i(industry)/s(stock): ') 

    industry_data_ready=False
    stock_data_ready=False
    #分种类读取数据
    if (scope == 'i' and (not industry_data_ready)):
        industry_data_ready=True
        industry_code_namedict=stock_basic.get_code_namedict(stock_basic.INDASTRY)
        industry_dict=stock_basic.get_datadict(industry_code_namedict.keys(),'D:\python_project\source_data\industrydata',userows=datalen,columns=['amt','close'])
        for key in industry_dict.keys():
            industry_dict[key].columns=[key+'amt',key]
        industry_close_df=pd.concat([industry_dict[key][key] for key in industry_dict.keys()],axis=1)
    elif (scope =='s' and (not stock_data_ready)):  
        stock_data_ready=True
        stock_code_namedict=stock_basic.get_code_namedict(stock_basic.STOCK)
        stock_dict=stock_basic.get_datadict(stock_code_namedict.keys(),'D:\python_project\source_data\data',userows=datalen,usecols=[0,2])
        for key in stock_dict.keys():
            stock_dict[key].columns=[key]#
        stock_close_df=pd.concat([stock_dict[key] for key in stock_dict.keys()],axis=1)
    else:
        log("error scope")
        continue
    
    result=pd.DataFrame(columns=('code','name','date'))
    if scope =='i':
        target_df=industry_close_df
    elif scope== 's':
        target_df=stock_close_df
    target_data=target_df[target_code][(target_df.index>=begin_day) & (target_df.index<=end_day)].values
    target_data=target_data/target_data[0]#自创归一化，没用标准归一，试试效果
    target_data_len=len(target_data)
    for code in target_df.columns:
        sample_code_data=target_df[code]#样本股票数据      
        sample_code_data_len=len(sample_code_data)
        i=0
        while i+target_data_len<sample_code_data_len:
            sample_data=sample_code_data[i:i+target_data_len].values
            sample_data=sample_data/sample_data[0]
            Eudis=np.linalg.norm(target_data-sample_data)
            Eu_similarity=1/(1+Eudis)
            if Eu_similarity>0.78:
                print(Eu_similarity,"code:",code,sample_code_data.index[i])
                i=i+15
            else:
                i=i+1
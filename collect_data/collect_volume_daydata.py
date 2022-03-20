from WindPy import w
import datetime
import logging
import time
import csv
import os
# usedf=True以后有空改成直接生成df

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
logging.basicConfig(level=logging.INFO)

def log(info,level=logging.INFO):
    logging.log(level,time.strftime("%Y-%m-%d %H:%M:%S   ", time.localtime())+info)

def write_winddf(data,filepath):
    if data[0]==0:
        data[1].to_csv(filepath)
        log(filepath+'datalen:%d'%len(data[1]))
    else:
        log("%dError Message:"%data[0]+ data[1].iloc[0, 0])

def bianli(L):
    log(u"数组长度%d"%len(L))
    for member in L:
        print(member)

def remove_file_notin_daylist(path,daylist,filename_len=12):#删除日期列表之外的数据文件
    dirlist=os.listdir(path)
    for filename in dirlist:
        if len(filename)==filename_len:
            if filename[0:8] in daylist:
                continue
        os.remove("%s/%s"%(path,filename))
        log(u"删除%s"%filename)


w.start() # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒  
log("WIND isconnect：%s"%w.isconnected())
today=(datetime.datetime.now()-datetime.timedelta(hours=21)).strftime("%Y%m%d")#日期字符串格式统一为20200202,21点前获得的数据可能不全
lasttday=w.tdaysoffset(0, today, "").Times[0].strftime("%Y%m%d")#最近的交易日

#所需的各个模块的代码列表
Indexcode_list=["000001.SH","000688.SH","000300.SH","000852.SH","000905.SH","399100.SZ","399102.SZ","399001.SZ","399006.SZ","399673.SZ"]#获取指数代码列表
industrycode_list=w.wset("sectorconstituent","date=%s;sectorid=a39901012g000000;field=wind_code"%today).Data[0]#获取行业代码列表
stockcode_list=w.wset("sectorconstituent","date=%s;sectorid=a001010100000000;field=wind_code"%today).Data[0]#获取股票代码列表

#获取指数，板块代码-名称字段对
Indexcode_name_data=w.wss(Indexcode_list, "sec_name","ShowBlank=NAN",usedf=True)#获取指数代码，名称
write_winddf(Indexcode_name_data,"../../source_data/code_name/Indexcode_name_list.csv")
industrycode_name_data=w.wss(industrycode_list, "sec_name","ShowBlank=NAN",usedf=True)#获取行业代码，名称
write_winddf(industrycode_name_data,"../../source_data/code_name/industrycode_name_list.csv")
#获取股票所有需要的相关信息
#sec_name 证券名称
#pct_chg  涨幅
#amt  成交额
#close  收盘价
#ipo_date  上市日期
#concept  概念板块
#mkt_cap_ard  总市值
#val_pe_deducted_ttm  市盈率ttm
#province  省份
#city  城市
code_name_data=w.wss(stockcode_list, "sec_name,pct_chg,amt,close,ipo_date,concept,mkt_cap_ard,val_pe_deducted_ttm,province,city","tradeDate=%s;ShowBlank=NAN;industryStandard=3"%lasttday,usedf=True)
write_winddf(code_name_data,"../../source_data/code_name/code_name_list.csv")

#生成最近daylistlenth个交易日的数组
daylistlenth=360
endday=today
beginday=w.tdaysoffset(-daylistlenth, endday, "").Times[0]
daylist=w.tdays(beginday,endday, "").Times
daylist=[d.strftime("%Y%m%d") for d in daylist]#优先最新日期
daylist.sort(reverse = True)

##获取各代码信息并记录
#从万得获取指数信息
log("Index begin")
path="../../source_data/Indexdata"
for code in Indexcode_list:
    stock_data=w.wsd(code, "amt,close,", min(daylist), max(daylist), "ShowBlank=nan;PriceAdj=F",usedf=True)#成交额，收盘价
    write_winddf(stock_data,"%s/%s.csv"%(path,code))

#从万得获取行业信息
log("industry begin")
path="../../source_data/industrydata"
remove_file_notin_daylist(path,daylist)
dirlist=os.listdir(path)
for day in daylist:    
    if day+".csv" in dirlist:
        continue    
    stock_data=w.wss(industrycode_list, "amt,close,volume,free_turn_n,turn","tradeDate=%s;cycle=D;priceAdj=F;ShowBlank=nan"%day,usedf=True)#成交额，收盘价
    write_winddf(stock_data,"%s/%s.csv"%(path,day))

#从万得获取股票信息
log("stock begin")
path="../../source_data/data"
remove_file_notin_daylist(path,daylist)
dirlist=os.listdir(path)
for day in daylist:    
    if day+".csv" in dirlist:
        continue    
    stock_data=w.wss(stockcode_list, "amt,close,pct_chg,mkt_cap_ard","tradeDate=%s;cycle=D;priceAdj=B;ShowBlank=nan"%day,usedf=True)#成交额，收盘价,涨幅，市值(这里用后复权方便回测，计算)
    write_winddf(stock_data,"%s/%s.csv"%(path,day))


w.stop()
os.chdir(maincwd)
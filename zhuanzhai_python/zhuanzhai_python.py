import os
from WindPy import w
import datetime
import time
import csv
import pandas as pd

def get_zhuanzhai_by_yijialv(WindPydata,yijialvmax,chengjiaoemin,ifprint=False,yijialvmin=-100,chengjiaoemax=99999999999):#通过溢价率，成交额筛选转债
    data=WindPydata
    stockcodes=[]
    if data.ErrorCode==0:
        for index,code in enumerate(data.Codes):       
            if yijialvmin<data.Data[1][index]<yijialvmax:#筛选溢价率
                if chengjiaoemin<data.Data[2][index]<chengjiaoemax:#筛选成交额                   
                    stockcodes.append([data.Data[4][index].strftime("%Y%m%d"),float("%.2f"%(data.Data[5][index]/100000000)),data.Data[6][index],data.Data[3][index],float("%.2f"%(data.Data[1][index])),float("%.2f"%(data.Data[2][index]/100000000)),float("%.2f"%(data.Data[7][index]))])
    else:
        print(u"获取数据失败，错误代码：%s 错误内容：%s" %(data.ErrorCode,data.Data))#输出编码为u的错误信息
    if ifprint:
        bianli(stockcodes)
    return stockcodes;

def get_zhuanzhai_by_30dayvolume(WindPydata,volume_times,ifprint=False):#通过单日放量筛选转债
    data=WindPydata
    stockcodes=[]
    if data.ErrorCode==0:
        for index,code in enumerate(data.Codes):
            datalen=len(data.Data[index])
            if datalen<=20:
                continue
            volume_new=data.Data[index][-1]
            volume_avg=sum(data.Data[index])/datalen
            if volume_new>volume_avg*volume_times:#如果最新成交量大于阈值
                stockcodes.append(code)
    else:
        print(u"获取数据失败，错误代码：%s 错误内容：%s" %(data.ErrorCode,data.Data))#输出编码为u的错误信息
    if ifprint:
        bianli(stockcodes)
    return stockcodes;

def bianli(L):
    print(u"数组长度%d"%len(L))
    for member in L:
        print(member)

def get_tday_byoffset(WindPy,date,offset=0):#获取以date为基础的交易日，offset为偏移日期可为负数，即向前推，offset为0指向离date最近的上一个交易日
    date=WindPy.tdaysoffset(offset,date)
    if date.ErrorCode==0:
        return date.Times[0].strftime("%Y%m%d");
    else:
        print(u"获取数据失败，错误代码：%s 错误内容：%s" %(date.ErrorCode,date.Data))
        return datetime.datetime.now().strftime("%Y%m%d");

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])

#日期字符串格式统一为20200202
today=datetime.datetime.now().strftime("%Y%m%d")
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
#获取转债代码列表
w.start() # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒  
print(w.isconnected())
today=w.tdaysoffset(0, today, "").Times[0].strftime("%Y%m%d")#最近的交易日
zhuanzhaicodes=w.wset("sectorconstituent","date=%s;sectorid=a101020600000000;field=wind_code"%today)
if zhuanzhaicodes.ErrorCode!=0:
    print(u"获取数据失败，错误代码：%s 错误内容：%s" %(zhuanzhaicodes.ErrorCode,zhuanzhaicodes.Data))
zhuanzhaistr=",".join(zhuanzhaicodes.Data[0])

#
wss_option="tradeDate=%s;cycle=D;ShowBlank=0"%today#空值填充0
yijialv_data=w.wss(zhuanzhaistr, "underlyingcode,convpremiumratio,amt,underlyingname,clause_conversion_2_swapsharestartdate,clause_conversion2_bondlot,sec_name,close",wss_option)#0正股代码，1转股溢价率，2成交额，3正股名称，4转股日期，5未转股余额，6证券简称,7收盘价

stockcodes=get_zhuanzhai_by_yijialv(yijialv_data,20,1,False)#第二个参数转股溢价率最大值，#第三个参数成交额最小值

stock_df=pd.DataFrame(stockcodes,columns=['转股日期','未转股额','转债名称','正股名称','转股溢价','成交额','价格'])
stock_df.sort_values(by='成交额',ascending=False)
stock_df.sort_values(by='转股溢价',ascending=True)

w.stop()
os.chdir(maincwd)
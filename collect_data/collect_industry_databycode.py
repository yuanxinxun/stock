from WindPy import w
import datetime
import logging
import time
import csv
import os

maincwd=os.getcwd()
os.chdir(os.path.split(os.path.realpath(__file__))[0])
logging.basicConfig(level=logging.INFO)
def log(info,level=logging.INFO):
    logging.log(level,time.strftime("%Y-%m-%d %H:%M:%S   ", time.localtime())+info)

today=(datetime.datetime.now()-datetime.timedelta(hours=21)).strftime("%Y%m%d")#日期字符串格式统一为20200202,21点前获得的数据可能不全
w.start() # 默认命令超时时间为120秒，如需设置超时时间可以加入waitTime参数，例如waitTime=60,即设置命令超时时间为60秒  
log("WIND isconnect：%s"%w.isconnected())
industrycode_list=w.wset("sectorconstituent","date=%s;sectorid=a39901011i000000;field=wind_code"%today).Data[0]#获取行业代码列表


#从万得获取行业信息
log("industry begin")
path='D:/python_project/source_data/industrydata_crowding'
for code in industrycode_list:
    data=w.wsd("858811.SI", "close,volume,turn,free_turn_n,amt", "2021-11-01", "2021-12-04", "unit=1;PriceAdj=B",usedf=True)
    if data[0]==0:
        data[1].to_csv("%s/%s.csv"%(path,code))
        log(code+'datalen:%d'%len(data[1]))
    else:
        log("Error Message:", data[1].iloc[0, 0])
dirlist=os.listdir(path)
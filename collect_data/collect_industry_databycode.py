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

today=(datetime.datetime.now()-datetime.timedelta(hours=21)).strftime("%Y%m%d")#�����ַ�����ʽͳһΪ20200202,21��ǰ��õ����ݿ��ܲ�ȫ
w.start() # Ĭ�����ʱʱ��Ϊ120�룬�������ó�ʱʱ����Լ���waitTime����������waitTime=60,���������ʱʱ��Ϊ60��  
log("WIND isconnect��%s"%w.isconnected())
industrycode_list=w.wset("sectorconstituent","date=%s;sectorid=a39901011i000000;field=wind_code"%today).Data[0]#��ȡ��ҵ�����б�


#����û�ȡ��ҵ��Ϣ
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
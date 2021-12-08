import os
import csv
import logging
import pandas as pd
data_path='D:\python_project\source_data\code_name\code_name_list.csv'
industrydata_path='D:\python_project\source_data\code_name\industrycode_name_list.csv'
Indexdata_path='D:\python_project\source_data\code_name\Indexcode_name_list.csv'

STOCK=0
INDASTRY=1
INDEX=2

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(levelname)s - %(message)s')
def log(info,level=logging.INFO):
    logging.log(level,info)

def get_code_namedf(data_tpye):
    path = {STOCK:data_path,
              INDASTRY:industrydata_path,
              INDEX:Indexdata_path}
    code_namedf = pd.read_csv(path[data_tpye],index_col=0,header=0)#类似文件指针，只能循环一次
    return code_namedf
    log('readover dictlen%d'%len(code_namedf))

#给传入的字典填充数据(df.append()很慢，尽量少用)
def get_datadict(keys,filepath,filldf=True,usecols=None,header=None,userows=9999999999,columns=None):
    code_dict=dict.fromkeys(keys)
    filelist=os.listdir(filepath)
    filelist.sort(reverse=False)#按名称升序排列
    for file in filelist[-userows:]:
        daydata=pd.read_csv(filepath+'/%s'%file,index_col=0,header=header,usecols=usecols,skip_blank_lines=True)
        log('read data '+file+' begin: datalen:%d'%len(daydata))
        for key in code_dict.keys():
            if (key in daydata.index)==False:
                daydata.loc[key]=[None for i in  daydata.columns]
            series1=daydata.loc[key]
            series1.name=pd.to_datetime(file[0:8])
            if code_dict[key] is None:
                code_dict[key]=[series1]
            else:
                code_dict[key].append(series1)

    log('to df and fill nadata begin')
    for key in code_dict.keys():
        code_dict[key]=pd.DataFrame(code_dict[key])
        if columns!=None:
            code_dict[key].columns=columns
        code_dict[key]=code_dict[key].fillna(method='bfill')
    log('to df and fill nadata over,datalen:%d'%len(code_dict))
    return code_dict


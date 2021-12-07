import os
import sys
from scipy import stats
#coding=utf-8
from WindPy import w
import numpy as np
import pandas as pd
import csv

filepath='D:/python_project/source_data/industrydata_crowding'
filelist=os.listdir(filepath)
datadict={}
for file in filelist:
    if len(file)>8:
        if file[-4:]==".csv":
            data=pd.read_csv(filepath+'/%s'%file,index_col=0,header=0,skip_blank_lines=True)
            datadict[file[:-4]]=data

quantiledict={}#[10�������ʷ�� 95%,20��ƽ������90%,40��ɽ������̼����ϵ��95%]
for code in datadict.keys():
    data=datadict[code]

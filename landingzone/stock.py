# -*- coding:utf-8 -*-
from __future__ import division
from urllib import request
from struct import unpack
import mysql
import datetime
import os,glob,re
import operator as op
from multiprocessing import Process,freeze_support
import numpy as np
import pandas as pd

###############################################################################
# name      : stock.py
# author    : awen.zhu@hotmail.com
# created   : 2017-10-10
# purpose   : the script extracts tdx.com.cn's data files and then 
#             parse/load it into database
# changelist: 2018/2/25 python2.7 to python3.6
# copyright : copyright (c) zhuyunsheng awen.zhu@hotmail.com all rights received  
################################################################################

class istock(object):
    def __init__(self,):
        self.urlbase="http://hq.sinajs.cn/list=%s"
        self.watchlist=['sh600050','sz300494','sh600875','sz000598','sh600458','sz002433']
        self.multi=4
        self.curraccount={"avaliablebalance":100000,"currdate":datetime.datetime.strptime('2017-09-12','%Y-%m-%d'),'sh600050':{'totalamt':0,"totalprice":0,"availableamt":0,"currops":[]}}
        
    def _getStockInfo(self):
        data = request.urlopen(self.urlbase%','.join(self.watchlist))
        for l in data.readlines():
            print ( l.decode('gb18030').strip() )
            #for e in l.split(','):print e.decode('gb18030')
    def stock1day(self,md=None):
        print ("start")
        self.dfs=r'C:\zd_ztzq\vipdoc\*\lday\*.day'
        self.alldatafiles = glob.glob(self.dfs)   
        print (self.alldatafiles)
        for f in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
            with open(f,'rb') as fh:
                print ( "processing with data file : %s"%f )
                scode = os.path.basename(f).split('.')[0]
                with mysql.mysql() as db:
                    fc = fh.read()
                    d=[]
                    db._cursor.execute("""delete from tb_stk_1day where scode = '{}'""".format(scode))
                    db._conn.commit()
                    firstrow=0
                    lastema12,lasteam26,lastdea=0,0,0
                    while fc:
                        rawdata = unpack('IIIIIfII',fc[:32])
                        sdate = datetime.datetime.strptime(str(rawdata[0]),'%Y%m%d')
                        sopen = float(rawdata[1]/100)
                        shigh = float(rawdata[2]/100)
                        slow = float(rawdata[3]/100)
                        sclose = float(rawdata[4]/100)
                        samt  = int(rawdata[5])
                        svol = int(rawdata[6])
                        if firstrow == 0:
                            ema12,ema26,dif,dea = sclose,sclose,0,0
                        else:
                            ema12 = (2*sclose+(12-1)*lastema12)/(12+1)
                            ema26 = (2*sclose+(26-1)*lasteam26)/(26+1)
                            dif =  ema12 - ema26
                            dea = (2*dif + (9-1)*lastdea)/(9+1)
                        macd = 2*(dif - dea)
                        lastema12 = ema12
                        lasteam26 = ema26
                        lastdea = dea
                        firstrow += 1
                        d.append((scode,sdate,sopen,shigh,slow,sclose,samt,svol,round(ema12,2),round(ema26,2),round(dif,2),round(dea,2),round(macd,2)))
                        fc = fc[32:]
                    if d:
                        db._cursor.executemany("insert into tb_stk_1day values(?,?,?,?,?,?,?,?,?,?,?,?,?)",d)
                        db._conn.commit()
        print ("well done!")
    def f10(self,md=None):
        with open('e:/600362.txt','rb') as f:
            txt = f.read().decode('gb18030')
            print ( type(txt) )
            print ( re.findall(u'<!\S公司概况>(.*)<!C.*>',txt,re.RegexFlag.S)[0] )
    def stock1min(self,md=None):
        self.dfs=r'C:\zd_ztzq\vipdoc\*\minline\*.lc1'
        self.alldatafiles = glob.glob(self.dfs)
        with mysql.mysql() as db:
            for fl in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
                scode=os.path.basename(fl).split('.')[0]
                with open(fl,'rb') as f:
                    print ("start process file : %s"%fl)
                    fc = f.read()
                    d=[]
                    sql="""select ifnull(max(sdate),str_to_date('1980-01-01 12:12:12','%%Y-%%m-%%d %%H:%%M:%%S')) from tb_stk_1min where scode = '%s'"""%scode
                    maxdate = db._cursor.execute(sql).fetchone()[0]
                    if maxdate is None: maxdate = datetime.datetime.strptime('1980-01-01 10:10:10','%Y-%m-%d %H:%M:%S')
                    if datetime.datetime.today() > maxdate:
                        while fc:
                            rawdata = unpack('hhfffffii',fc[:32])
                            sdate = datetime.datetime.strptime("%s-%02d-%02d %02d:%02d:%02d"%(int(rawdata[0]/2048)+2004,int(op.mod(rawdata[0],2048)/100),op.mod(op.mod(rawdata[0],2048),100),int(rawdata[1]/60),op.mod(rawdata[1],60),0),'%Y-%m-%d %H:%M:%S')                            
                            ropen,rhigh,rlow,rclose,ramt,rvol = "%.2f"%rawdata[2],"%.2f"%rawdata[3],"%.2f"%rawdata[4],"%.2f"%rawdata[5],"%.2f"%rawdata[6],"%d"%rawdata[7]
                            if sdate > maxdate:
                                d.append((scode,sdate,ropen,rhigh,rlow,rclose,ramt,rvol))
                                #print scode,datetime.datetime.strptime(sdate,'%Y-%m-%d %H:%M:%S'),ropen,rhigh,rlow,rclose,ramt,rvol
                            fc = fc[32:]
                        if d:
                            db._cursor.executemany("insert into tb_stk_1min values(?,?,?,?,?,?,?,?)",d)
                            db._conn.commit()

    def run(self):
        for i in range(self.multi):
            p=Process(target=self.stock1day,args=(i,))
            p.start()
        p.join()
    
if __name__ == "__main__":
    freeze_support()
    istk = istock()
    #istk._getStockInfo()
    #istk.stock1day(0)
    #istk.f10()
    istk.run()
    #istk.stock1min()
    #istk.backtrace()
    #istk.buy(scode='sh600050',amt=10000,price=7.11,opdate=datetime.datetime.strptime('2017-09-11','%Y-%m-%d'))
    
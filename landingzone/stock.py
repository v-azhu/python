# -*- coding:utf-8 -*-
from __future__ import division
from urllib2 import urlopen
from struct import unpack
import mysql
import datetime
import os,glob,re
import operator as op
from multiprocessing import Process,freeze_support

###############################################################################
# name      : stock.py
# author    : carl_zys@163.com
# created   : 2017-10-10
# purpose   : the script extracts tdx.com.cn's data files and then 
#             parse/load it into database
# copyright : copyright (c) zhuyunsheng carl_zys@163.com all rights received  
################################################################################

class istock(object):
    def __init__(self,):
        self.urlbase="http://hq.sinajs.cn/list=%s"
        self.watchlist=['sh600050','sz300494','sh600875','sz000598','sh600458','sz002433']
        self.multi=4
    def _getStockInfo(self):
        data = urlopen(self.urlbase%','.join(self.watchlist))
        for l in data.readlines():
            print l.decode('gb18030').strip()
            #for e in l.split(','):print e.decode('gb18030')
    def stock1day(self,md=None):
        self.dfs=r'E:\zd_ztzq\vipdoc\*\lday\*.day'
        self.alldatafiles = glob.glob(self.dfs)        
        for f in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
            with open(f,'rb') as fh:
                print "processing with data file : %s"%f
                with mysql.mysql() as db:
                    fc = fh.read()
                    d=[]
                    maxdate = db._cursor.execute("""select ifnull(max(sdate),str_to_date('1980-01-01','%%Y-%%m-%%d')) from tb_stk_1day where scode = '%s'"""%os.path.basename(f).split('.')[0]).fetchone()[0]                    
                    if maxdate is None: maxdate = datetime.date.strptime('1980-01-01','%Y-%m-%d')
                    if datetime.date.today() > maxdate:
                        while fc:
                            rawdata = unpack('IIIIIfII',fc[:32])
                            if datetime.datetime.strptime(str(rawdata[0]),'%Y%m%d') > datetime.datetime(maxdate.year, maxdate.month, maxdate.day):
                                d.append( (os.path.basename(f).split('.')[0],datetime.datetime.strptime(str(rawdata[0]),'%Y%m%d'),float(rawdata[1]/100),float(rawdata[2]/100),float(rawdata[3]/100),float(rawdata[4]/100), int(rawdata[5]),int(rawdata[6]) ) )
                            fc = fc[32:]
                        if d:
                            db._cursor.executemany("insert into tb_stk_1day values(?,?,?,?,?,?,?,?)",d)
                            db._conn.commit()
    def f10(self,md=None):
        with open('e:/600362.txt','rb') as f:
            txt = f.read().decode('gb18030')
            print type(txt)
            print re.findall(u'<!\S公司概况>(.*)<!C.*>',txt,re.S)[0]
    def stock1min(self,md=None):
        self.dfs=r'E:\zd_ztzq\vipdoc\*\minline\*.lc1'
        self.alldatafiles = glob.glob(self.dfs)
        with mysql.mysql() as db:
            for fl in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
                scode=os.path.basename(fl).split('.')[0]
                with open(fl,'rb') as f:
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
    def backtrace(self,):
        scode='sh600050'
        startdate=datetime.datetime.strptime('2017-09-10 00:00:00','%Y-%m-%d %H:%M:%S')
        enddate = datetime.datetime.now()
        nextday = startdate+datetime.timedelta(days=1)
        maxclose,minclose,avgclose,minsdate = self.getndaysavgprice()
        stockamt,maxstockamt = 0,30000
        
        with mysql.mysql() as db:
            while nextday < enddate:
                sql="select * from tb_stk_1min where scode = '%s' and sdate > '%s' and sdate < '%s' order by sdate"%(scode,startdate,nextday)
                action,btime,price = None,None,None
                for r in db._cursor.execute(sql).fetchall():
                    if r[5] > avgclose and stockamt < maxstockamt and action <> "buy":
                        action, price,btime,stockamt = "buy", r[5],r[1],(stockamt if stockamt<>0 else maxstockamt)
                    elif r[5] < avgclose and stockamt > 0 and action <> "sell":
                        action, price,btime,stockamt = "sell", r[5],r[1],int(stockamt-(stockamt/2))
                if btime is not None: print btime,action, price,stockamt,price*stockamt
                startdate = nextday
                nextday = startdate+datetime.timedelta(days=1)
    def getndaysavgprice(self,scode='sh600050',days=20):
        with mysql.mysql() as db:
            sql="""select max(rclose) maxclose,min(rclose) minclose,avg(rclose) avgclose,min(sdate) minsdate from tb_stk_1min where scode = '%s' and sdate > date_sub(sysdate(),interval %d day)
            """%(scode,days)
            rs = db._cursor.execute(sql).fetchone()
            return rs
    def run(self):
        for i in range(self.multi):
            p=Process(target=self.stock1min,args=(i,))
            p.start()
        p.join()
        
if __name__ == "__main__":
    freeze_support()
    istk = istock()
    #istk._getStockInfo()
    #istk.stock1day(1)
    #istk.f10()
    #istk.run()
    #istk.stock1min()
    istk.backtrace()
    
# -*- coding:utf-8 -*-
from __future__ import division
from urllib2 import urlopen
from struct import unpack
import mysql
import datetime
import os,glob
from multiprocessing import Process,freeze_support

class istock(object):
    def __init__(self,):
        self.urlbase="http://hq.sinajs.cn/list=%s"
        self.watchlist=['sh600050','sz300494','sh600875','sz000598','sh600458','sz002433']
        self.dfs=r'E:\zd_ztzq\vipdoc\*\lday\*.day'
        self.alldatafiles = glob.glob(self.dfs)
        self.multi=4
    def _getStockInfo(self):
        data = urlopen(self.urlbase%','.join(self.watchlist))
        for l in data.readlines():
            print l.decode('gb18030').strip()
            #for e in l.split(','):print e.decode('gb18030')
    def _histdataextract(self,md=None):
        for f in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
            with open(f,'rb') as fh:
                with mysql.mysql() as db:
                    fc = fh.read()
                    d=[]
                    while fc:
                        rawdata = unpack('IIIIIfII',fc[:32])
                        d.append( (os.path.basename(f).split('.')[0],datetime.datetime.strptime(str(rawdata[0]),'%Y%m%d'),float(rawdata[1]/100),float(rawdata[2]/100),float(rawdata[3]/100),float(rawdata[4]/100), int(rawdata[5]),int(rawdata[6]) ) )
                        fc = fc[32:]
                    db._cursor.executemany("insert into tb_stk_1day values(?,?,?,?,?,?,?,?)",d)
                    db._conn.commit()
    def dailyload(self,md=None):
        pass
    def run(self):
        for i in range(self.multi):
            p=Process(target=self._histdataextract,args=(i,))
            p.start()
        p.join()
if __name__ == "__main__":
    freeze_support()
    istk = istock()
    #istk._getStockInfo()
    #istk._histdataextract('e:/sh600050.day')
    istk.run()
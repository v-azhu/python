# -*- coding:utf-8 -*-
from prettytable import PrettyTable
import pandas as pd
import numpy as np
from urllib import request
from datetime import datetime
###############################################################################
# name      : stock.py
# author    : awen.zhu@hotmail.com
# created   : 2017-10-10
# purpose   : the script to analyzing stock info by user defined method 
# changelist: 
# copyright : copyright (c) zhuyunsheng awen.zhu@hotmail.com all rights received  
################################################################################

class stockanalysis(object):
    def __init__(self):
        self.srcdir=r'C:\zd_ztzq\vipdoc'
        self.urlbase="https://hq.sinajs.cn/list=%s"
    def getData(self,scode=None):
        """
        read source data as pandas data frame
        """
        f = self.srcdir+'\\'+scode[:2]+'\\lday\\'+scode+'.day'
        dstruck = np.dtype([('sdate', 'i4'), ('sopen', 'i4'), ('shigh', 'i4'), ('slow', 'i4'), ('sclose', 'i4'),('samt', 'f4'),('svol','i4'),('skept','i4')])
        dat = np.fromfile(f,dstruck)
        df = pd.DataFrame(dat.tolist(),columns=dat.dtype.names)
        df['sopen'] = df['sopen']/100
        df['shigh'] = df['shigh']/100
        df['slow'] = df['slow']/100
        df['sclose'] = df['sclose']/100
        return df
    def getRealTimeData(self,scode=None):
        data = request.urlopen(self.urlbase%scode)
        return ( str(data.readlines()).split(',')[3]  )
    def getTecIndexes(self,scode=None,sdate=20171201):
        """
        # 12日EMA的算式为 
        # EMA（12）=前一日EMA（12）×11/13＋今日收盘价×2/13 
        # 26日EMA的算式为 
        # EMA（26）=前一日EMA（26）×25/27＋今日收盘价×2/27 
        """
        sindex={}
        df = self.getData(scode=scode)
        for i in range(len(df)):
            sindex[df.ix[i,'sdate']]={'ema12':0,'ema26':0,'dif':0,'dea':0,'macd':0}
            if i==0:  
                sindex[df.ix[i,'sdate']]['ema12'] = df.ix[i,'sclose']
                sindex[df.ix[i,'sdate']]['ema26'] = df.ix[i,'sclose']                
            if i>0:  
                sindex[df.ix[i,'sdate']]['ema12'] = round(float ( (2*df.ix[i,'sclose']+(12-1)*sindex[df.ix[i-1,'sdate']]['ema12'])/(12+1)),2)
                sindex[df.ix[i,'sdate']]['ema26'] = round(float ( (2*df.ix[i,'sclose']+(26-1)*sindex[df.ix[i-1,'sdate']]['ema26'])/(26+1)),2)
                sindex[df.ix[i,'sdate']]['dif'] =  round(float ( sindex[df.ix[i,'sdate']]['ema12']-sindex[df.ix[i,'sdate']]['ema26'] ),2)
                sindex[df.ix[i,'sdate']]['dea'] = round(float ( (2*sindex[df.ix[i,'sdate']]['dif'] + (9-1)*sindex[df.ix[i,'sdate']]['dea'])/(9+1)),2)
            sindex[df.ix[i,'sdate']]['macd'] = round(float ( 2*(sindex[df.ix[i,'sdate']]['dif'] - sindex[df.ix[i,'sdate']]['dea'])),2)
        if sdate in sindex.keys(): 
            return sindex[sdate]
        else:return None
    def nDaysRiseHistLookup(self,scode='sh600458',startdate=19990101,ndays=3):
        """
        #计算开始日期向后n天的涨副，例如给定2011-03-11,则计算从2011-03-11往后ndays的涨副
        """
        try:
            df = self.getData(scode=scode)
            rs = df.ix[df.sdate<=startdate][-ndays-1:]
            if len(rs) > 1:
                return round((rs.iloc[ndays-1].sclose-rs.iloc[0].sclose)/rs.iloc[0].sclose,2)
            else: return 0
        except:pass
    def lastNDaysRiseLookup(self,scode='sh600458',ndays=3):
        """
        #计算开始日期向后n天的涨副，初始日期为当天
        """
        currdate = int(datetime.strftime(datetime.today(),'%Y%m%d'))
        df = self.getData(scode=scode)
        rs = df.ix[df.sdate<=currdate][-ndays:]
        currprice = float( self.getRealTimeData(scode) )
        return (currprice-rs.iloc[0].sclose)/rs.iloc[0].sclose
     
    def getNdaysRise(self,scode='sh600458',ndays=3,rise=0.1,nextdays=30):
        """
        identifies the stock which risen over x% for n days, then get the price after m days.(得到连续n天上涨或下跌超过x%的股票，基m天之后的价格)
        """
        firstdayprice,thirddayprice,nextdaysprice = 0,0,0
        firstdate,thirddate='',''
        #pt = PrettyTable(('TheFirstRisenDate','TheFirstRisenPrice(openPrice)','TheThirdRisenDate','TheThirdRisenPrice(closePrice)','IncreasingRiseRate','The30DaysDate','The30DaysPrice(closeprice)','RisenTotal','RisenRate'))
        #pt = PrettyTable(('第一次上涨日期','第一次上涨时价格','第三次上涨日期','第三次上涨价格','第30个交易日日期','第30个交易日价格','累计上涨金额','上涨百分比'))
        df = pd.DataFrame(self.getData(scode=scode))
        rs=[('TheFirstRisenDate','TheFirstRisenPrice(openPrice)','TheThirdRisenDate','TheThirdRisenPrice(closePrice)','IncreasingRiseRate','The30DaysDate','The30DaysPrice(closeprice)','RisenTotal','RisenRate')]
        for i, r in df.iterrows():
            if i % ndays == 1 and firstdayprice == 0 : firstdayprice,firstdate = r.sopen, r.sdate
            if i % ndays == 0 and thirddayprice == 0 : 
                thirddayprice,thirddate = r.sclose,r.sdate
                nextdaysprice = df.iloc[i+nextdays-ndays].sclose if i+nextdays<len(df) else df.iloc[-1].sclose
                next30daysdate = df.iloc[i+nextdays-ndays].sdate if i+nextdays<len(df) else df.iloc[-1].sdate
                if firstdayprice !=0 and (thirddayprice - firstdayprice )/firstdayprice  > rise and rise > 0:
                    increasingriserate = '%.2f%%' % ( ((thirddayprice - firstdayprice )*100)/firstdayprice )                        
                    rs.append((firstdate,firstdayprice,thirddate,thirddayprice,increasingriserate,next30daysdate,nextdaysprice, ( nextdaysprice-thirddayprice ),'%.2f%%' % ((nextdaysprice-thirddayprice)*100/thirddayprice)))                                           
                if firstdayprice !=0 and (thirddayprice - firstdayprice )/firstdayprice < rise and rise < 0:
                    increasingriserate = '%.2f%%' % ( ((thirddayprice - firstdayprice )*100)/firstdayprice )
                    rs.append((firstdate,firstdayprice,thirddate,thirddayprice,increasingriserate,next30daysdate,nextdaysprice, ( nextdaysprice-thirddayprice ),'%.2f%%' % ((nextdaysprice-thirddayprice)*100/thirddayprice)))
                nextdaysprice,firstdayprice,thirddayprice = 0,0,0
        dfrs = pd.DataFrame(rs[1:],columns=rs[0])
        dfrsh = dfrs.ix[dfrs.RisenTotal > 0]
        dfrsl = dfrs.ix[dfrs.RisenTotal < 0]
        pt = PrettyTable(rs[0])
        for r in dfrs.itertuples(): pt.add_row( r[1:] )
        #if len(dfrsh) !=0 and len(dfrsl)/len(dfrsh) < 0.4 : 
        print ('scode=%s\n'%scode,pt,'\nTotalRows:'+str(len( dfrs )))
    def simulation(self,scode=None,startdate=None,initamount=1000000):
        """
        # 以100万初始资金模拟炒股，连续3个交易日涨副超过10%时全仓买入，跌过8%时止损卖出。忽略期间的交易手续费，不考虑100股的整数倍，从某个日期开始回归测试至当前日期，
        """
        df = self.getData(scode=scode)
        df = df.ix[df.sdate>=startdate]
        holdstock,unusedamount,totalamount=0,0,initamount
        tradedate = None
        risen=0
        holdprice = 0
        maxAmount,minAmount,currentamount=0,0,0
        #pt = PrettyTable(('TheFirstRisenDate','TheFirstRisenPrice(openPrice)','TheThirdRisenDate','TheThirdRisenPrice(closePrice)','IncreasingRiseRate','The30DaysDate','The30DaysPrice(closeprice)','RisenTotal','RisenRate'))
        #pt = PrettyTable(('第一次上涨日期','第一次上涨时价格','第三次上涨日期','第三次上涨价格','第30个交易日日期','第30个交易日价格','累计上涨金额','上涨百分比'))
        for r in df.iterrows():
            avgprice = (r[1].shigh+r[1].slow) / 2 
            risen = self.nDaysRiseHistLookup(scode, r[1].sdate, 3)
            if not risen:continue
            if risen > 0.08:
                # buy
                holdstock = holdstock + int( totalamount / avgprice )
                totalamount = totalamount-( (int( totalamount / avgprice ) ) *avgprice)
                tradedate = r[1].sdate
                holdprice = avgprice
                action='Buy'
            elif risen < -0.06:
                # sell
                totalamount = totalamount + (holdstock * avgprice)
                holdstock = 0
                tradedate = r[1].sdate
                holdprice = 0
                action='Sell'
            else:
                tradedate = r[1].sdate
                action='N/A'
            currentamount = totalamount+(holdprice*holdstock)
            maxAmount = currentamount if currentamount > maxAmount else maxAmount
            minAmount = currentamount if currentamount < initamount else minAmount
            if action != 'N/A':
                print ("Scode=%s,Tradedate=%s,Action=%s,Risen=%.2f,HoldStock=%d,TotalAmount=%.2f,CurrentAmount=%.2f,maxAmount=%.2f,minAmount=%.2f"%(scode,tradedate,action,risen,holdstock,totalamount,currentamount,maxAmount,minAmount) )
                    
if __name__ == "__main__":
    s = stockanalysis()
    #s.getTecIndexes(scode='sz002900')
    #s.getData(scode='sz000598')
    #with mysql.mysql() as db:
        #for scode in db._cursor.execute("select distinct scode from stdb.tb_stk_1day where substr(scode,1,3) in ('sz0') ").fetchall():
            #s.getNdaysRise(scode=scode[0],nextdays=30,rise=0.1)
            #s.simulation(scode=scode[0],startdate=20170101)
    #s.getClosePriceByDate()
    #s.getNdaysRise(scode='sz000727',nextdays=30,rise=0.1)
    #s.simulation(scode='sz300494',startdate=20170101)
    s.lastNDaysRiseLookup(scode='sz002906')
    #s.nDaysRiseHistLookup(scode='sz000727',startdate=20150714,ndays=3)
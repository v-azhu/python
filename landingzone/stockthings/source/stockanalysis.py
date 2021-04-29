# -*- coding:utf-8 -*-
from prettytable import PrettyTable
import pandas as pd
import numpy as np
from urllib import request
from datetime import datetime,timedelta
import re
import mysql
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
        self.holiday=[20180101,20180215,20180216,20180219,20180220,20180221,20180405,20180406,20180501,20180618,20180924,20181001,20181002,20181003,20181004,20181005]
        
    def getData(self,scode=None):
        """
        read source data as pandas data frame
        """
        f = self.srcdir+'\\'+scode[:2]+'\\lday\\'+scode+'.day'
        dstruck = np.dtype([('sdate', 'i4'), ('sopen', 'i4'), ('shigh', 'i4'), ('slow', 'i4'), ('sclose', 'i4'),('samt', 'f4'),('svol','i4'),('skept','i4')])
        rawdat = np.fromfile(f,dstruck)
        dat = rawdat.tolist()
        currdata = self.getRealTimeData(scode)
        if currdata is not None:
            currdata = currdata.tolist()
            df = pd.DataFrame(np.vstack((dat,currdata)),columns=rawdat.dtype.names)
        else:
            df = pd.DataFrame(self.dat,columns=self.rawdat.dtype.names)
        df['sopen'] = df['sopen']/100
        df['shigh'] = df['shigh']/100
        df['slow'] = df['slow']/100
        df['sclose'] = df['sclose']/100
        return df
    def getRealTimeData(self,scode=None):
        data = request.urlopen(self.urlbase%scode)
        data = re.findall('\"(.*?)\"',data.readlines()[0].decode('gb18030'))  
        if len(data[0]) > 0:
            items = data[0].split(',')
            realtimedata = np.array( [ (int(datetime.strftime(datetime.today(),'%Y%m%d')),int(float(items[1])*100),int(float(items[4])*100),int(float(items[5])*100),int(float(items[3])*100),round(float(items[9])),int(items[8]),0) ] )
            return realtimedata
        else: return None
    def getTecIndexes(self,scode=None,sdate=None):
        """
        # 12��EMA����ʽΪ 
        # EMA��12��=ǰһ��EMA��12����11/13���������̼ۡ�2/13 
        # 26��EMA����ʽΪ 
        # EMA��26��=ǰһ��EMA��26����25/27���������̼ۡ�2/27 
        """
        sindex={}
        df = self.getData(scode=scode)
        for i in range(len(df)):
            sindex[df.ix[i,'sdate']]={'ema12':0,'ema26':0,'dif':0,'dea':0,'macd':0}
            if i==0:
                sindex[df.ix[i,'sdate']]['ema12'] = df.ix[i,'sclose']
                sindex[df.ix[i,'sdate']]['ema26'] = df.ix[i,'sclose']
            if i>0:  
                sindex[df.ix[i,'sdate']]['ema12'] = round(float ( (2*df.ix[i,'sclose']+(12-1)*sindex[df.ix[i-1,'sdate']]['ema12'])/(12+1)),4)
                sindex[df.ix[i,'sdate']]['ema26'] = round(float ( (2*df.ix[i,'sclose']+(26-1)*sindex[df.ix[i-1,'sdate']]['ema26'])/(26+1)),4)
                sindex[df.ix[i,'sdate']]['dif'] =  round(float ( sindex[df.ix[i,'sdate']]['ema12']-sindex[df.ix[i,'sdate']]['ema26'] ),4)
                sindex[df.ix[i,'sdate']]['dea'] = round(float ( (2*sindex[df.ix[i,'sdate']]['dif'] + (9-1)*sindex[df.ix[i-1,'sdate']]['dea'])/(9+1)),4)
            sindex[df.ix[i,'sdate']]['macd'] = round(float ( 2*(sindex[df.ix[i,'sdate']]['dif'] - sindex[df.ix[i,'sdate']]['dea'])),4)
        if sdate in sindex.keys(): 
            return sindex[sdate]
        else:return None
    def istradeDate(self,checkdate=None):
        df = self.getData(scode='sh999999')
        df = df.ix[df.sdate==checkdate]
        holiday=[20180101,20180215,20180216,20180219,20180220,20180221,20180405,20180406,20180501,20180618,20180924,20181001,20181002,20181003,20181004,20181005]
        if df.empty:
            if checkdate in holiday or (datetime.strptime(str(checkdate),'%Y%m%d').weekday()) in (5,6):
                return (False)
            else:return (True)
        else: 
            return (True)
    def getPreviousTradeDate(self,sdate=20180305):
        checkdate=datetime.strptime(str(sdate),'%Y%m%d')
        for i in range(1,100,1):
            previousdate = int(datetime.strftime(checkdate-timedelta(days=i),'%Y%m%d'))
            if self.istradeDate(checkdate=previousdate):
                #print (previousdate)
                return previousdate
    def isMACDGoldenCross(self,scode=None,sdate=int(datetime.strftime(datetime.today(),'%Y%m%d'))):
        currentindexes = self.getTecIndexes(scode=scode,sdate=sdate)
        previouseindexes = self.getTecIndexes(scode=scode,sdate=self.getPreviousTradeDate(sdate))
        if currentindexes is not None and previouseindexes is not None:
            if previouseindexes['macd'] < 0 and currentindexes['macd'] > 0:
                return True
            else:
                return False
        else:
            return False
    def isMACDDeadCross(self,scode=None,sdate=int(datetime.strftime(datetime.today(),'%Y%m%d'))):
        currentindexes = self.getTecIndexes(scode=scode,sdate=sdate)
        previouseindexes = self.getTecIndexes(scode=scode,sdate=self.getPreviousTradeDate(sdate))
        if currentindexes is not None and previouseindexes is not None:
            if previouseindexes['macd'] > 0 and currentindexes['macd'] < 0:
                return True
            else:
                return False
        else:
            return False
    def nDaysRiseHistLookup(self,scode='sh600458',startdate=19990101,ndays=3):
        """
        #���㿪ʼ�������n����Ǹ����������2011-03-11,������2011-03-11����ndays���Ǹ�
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
        #���㿪ʼ�������n����Ǹ�����ʼ����Ϊ����
        """
        currdate = int(datetime.strftime(datetime.today(),'%Y%m%d'))
        df = self.getData(scode=scode)
        rs = df.ix[df.sdate<=currdate][-ndays:]
        currprice =  self.getRealTimeData(scode)
        currprice = currprice[0][4]/100
        return round((currprice-rs.iloc[0].sclose)/rs.iloc[0].sclose,2)
     
    def getNdaysRise(self,scode='sh600458',ndays=3,rise=0.1,nextdays=30):
        """
        identifies the stock which risen over x% for n days, then get the price after m days.(�õ�����n�����ǻ��µ�����x%�Ĺ�Ʊ����m��֮��ļ۸�)
        """
        firstdayprice,thirddayprice,nextdaysprice = 0,0,0
        firstdate,thirddate='',''
        #pt = PrettyTable(('TheFirstRisenDate','TheFirstRisenPrice(openPrice)','TheThirdRisenDate','TheThirdRisenPrice(closePrice)','IncreasingRiseRate','The30DaysDate','The30DaysPrice(closeprice)','RisenTotal','RisenRate'))
        #pt = PrettyTable(('��һ����������','��һ������ʱ�۸�','��������������','���������Ǽ۸�','��30������������','��30�������ռ۸�','�ۼ����ǽ��','���ǰٷֱ�'))
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
    def ndaysway(self,scode=None,startdate=None,initamount=1000000):
        """
        # ��100���ʼ�ʽ�ģ�⳴�ɣ�����3���������Ǹ�����10%ʱȫ�����룬����8%ʱֹ�������������ڼ�Ľ��������ѣ�������100�ɵ�����������ĳ�����ڿ�ʼ�ع��������ǰ���ڣ�
        """
        df = self.getData(scode=scode)
        df = df.ix[df.sdate>=startdate]
        holdstock,unusedamount,totalamount=0,0,initamount
        holdprice,risen=0,0
        tradedate = None
        maxAmount,minAmount,currentamount=0,0,0
        #pt = PrettyTable(('TheFirstRisenDate','TheFirstRisenPrice(openPrice)','TheThirdRisenDate','TheThirdRisenPrice(closePrice)','IncreasingRiseRate','The30DaysDate','The30DaysPrice(closeprice)','RisenTotal','RisenRate'))
        #pt = PrettyTable(('��һ����������','��һ������ʱ�۸�','��������������','���������Ǽ۸�','��30������������','��30�������ռ۸�','�ۼ����ǽ��','���ǰٷֱ�'))
        if len(df)<1: return
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
            #if action != 'N/A':
        if currentamount > 1000000:
            fl='output1.txt' 
        elif currentamount < 1000000:
            fl='output2.txt'
        else:fl='output3.txt'
        with open(fl,'a') as f:
            f.write(("Scode=%s,Tradedate=%s,Action=%s,Risen=%.2f,HoldStock=%d,Currprice=%.2f,TotalAmount=%.2f,CurrentAmount=%.2f,maxAmount=%.2f,minAmount=%.2f\n"%(scode,tradedate,action,risen,holdstock,avgprice,totalamount,currentamount,maxAmount,minAmount) ))
            print ("Scode=%s,Tradedate=%s,Action=%s,Risen=%.2f,HoldStock=%d,Currprice=%.2f,TotalAmount=%.2f,CurrentAmount=%.2f,maxAmount=%.2f,minAmount=%.2f"%(scode,tradedate,action,risen,holdstock,avgprice,totalamount,currentamount,maxAmount,minAmount) )
    def macdway(self,scode=None,startdate=None):
        """
        # ��100���ʼ�ʽ�ģ�⳴�ɣ��Ը��������ڿ�ʼ��MACD���ʱ���룬MACD����ʱ���µ�8%ʱֹ��������ز���Ե�������.
        """
        df = self.getData(scode=scode)
        df = df.ix[df.sdate>=startdate]
        holdstock,unusedamount,totalamount=0,0,1000000
        holdprice,risen=0,0
        tradedate = None
        maxAmount,minAmount,currentamount=0,0,0
        if len(df)<1: return
        for r in df.iterrows():
            avgprice = (r[1].shigh+r[1].slow) / 2
            if self.isMACDGoldenCross(scode=scode, sdate=int(r[1].sdate)):
                holdstock = holdstock + int( totalamount / avgprice )
                totalamount = totalamount-( (int( totalamount / avgprice ) ) *avgprice)
                tradedate = r[1].sdate
                holdprice = avgprice
                action='Buy'
            elif self.isMACDDeadCross(scode=scode, sdate=int(r[1].sdate)):
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
            minAmount = currentamount if currentamount < 1000000 else minAmount
            with open('sz.txt','a') as f:
                if action != 'N/A':
                    f.write ("Scode=%s,Tradedate=%s,Action=%s,HoldStock=%d,Currprice=%.2f,TotalAmount=%.2f,CurrentAmount=%.2f,maxAmount=%.2f,minAmount=%.2f\n"%(scode,tradedate,action,holdstock,avgprice,totalamount,currentamount,maxAmount,minAmount) )
    def macdwayfast(self,scode=None,startdate=None):
        """
        # ��100���ʼ�ʽ�ģ�⳴�ɣ��Ը��������ڿ�ʼ��MACD���ʱ���룬MACD����ʱ���µ�8%ʱֹ��������ز���Ե�������.
        """        
        with mysql.mysql() as db: 
            df = db._cursor.execute("select * from tb_stk_1day where scode = '{}' and sdate > '{}' order by sdate".format(scode,startdate)).fetchall()
        holdstock,unusedamount,totalamount=0,0,1000000
        holdprice,risen=0,0
        tradedate = None
        maxAmount,minAmount,currentamount=0,0,0
        if len(df)<1: return
        for i,r in enumerate(df[1::],1):
            avgprice = (r.shigh+r.slow) / 2
            if df[i-1].macd < 0 and r.macd >= 0:
                holdstock = holdstock + int( totalamount / avgprice )
                totalamount = totalamount-( (int( totalamount / avgprice ) ) *avgprice)
                tradedate = r.sdate
                holdprice = avgprice
                action='Buy'
            elif df[i-1].macd > 0 and r.macd <= 0:
                # sell
                totalamount = totalamount + (holdstock * avgprice)
                holdstock = 0
                tradedate = r.sdate
                holdprice = 0
                action='Sell'
            else:
                tradedate = r.sdate
                action='N/A'
            currentamount = totalamount+(r.sclose*holdstock)
            maxAmount = currentamount if currentamount > maxAmount else maxAmount
            minAmount = currentamount if currentamount < 1000000 else minAmount
            if action != 'N/A':
                self.pt.add_row((scode,tradedate,action,holdstock,r.sclose,totalamount,currentamount,maxAmount,minAmount))
        self.pt.add_row((scode,tradedate,'current',holdstock,df[-1].sclose,totalamount,df[-1].sclose*holdstock,maxAmount,minAmount))
    def macdgoldenwithbigvol(self,scode=None,sdate=None):
        with mysql.mysql() as db:
            sql="""select * from tb_stk_1day where scode = '{}' and sdate > '{}' order by sdate""".format(scode,sdate)
            df = pd.read_sql_query(sql, db._conn)
            volavg = df.svol.sum()/df.svol.count()
            for i,r in df[:-5].iterrows():
                if df.iloc[i-1].macd < 0 and df.iloc[i].macd >= 0 and df.iloc[i:i+5].svol.sum()/5 > 1.5*volavg:
                    print (r.sdate)
    def runmacd(self):
        import glob
        import os
        self.pt = PrettyTable(('Scode','Tradedate','Action','HoldStock','Currprice','TotalAmount','CurrentAmount','maxAmount','minAmount'))
        for f in glob.glob(s.srcdir+'\*\lday\*.day'):
            scode = os.path.basename(f).split('.')[0]            
            if scode[:2] in ('sh6'):
                s.macdwayfast(scode=scode, startdate='2017-12-01')
                self.pt.add_row(['-' for x in range(9)])
        with open('sh.txt','w') as f: f.write (str(self.pt))
if __name__ == "__main__":
    s = stockanalysis()
    #print ( s.getTecIndexes(scode='sz002900',sdate=20170925) )
    #s.getRealTimeData(scode='sz000598') 
    #s.getPreviousTradeDate()
    #s.getData(scode='sz000598')
    #s.getClosePriceByDate()
    #s.getNdaysRise(scode='sz000727',nextdays=30,rise=0.1)
    #s.ndaysway(scode='sz300494',startdate=20170101)
    #print ( s.lastNDaysRiseLookup(scode='sz002906') )
    #s.nDaysRiseHistLookup(scode='sz000727',startdate=20150714,ndays=3)
    #print ( s.isMACDGoldenCross(scode='sh600875',sdate=20180305) )
    #s.macdwayfast(scode='sh600875', startdate='2017-01-01')
    #s.runmacd()
    s.macdgoldenwithbigvol(scode='sh600458',sdate='2017-01-01')
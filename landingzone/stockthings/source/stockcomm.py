# -*- coding:utf-8 -*-
import pandas as pd
import numpy as np
from urllib import request
from datetime import datetime,timedelta
import re
import mysql
###############################################################################
# name      : stock.py
# author    : awen.zhu@hotmail.com
# created   : 2018-3-10
# purpose   : Basics module for operation
# changelist: 
# copyright : copyright (c) zhuyunsheng awen.zhu@hotmail.com all rights received  
################################################################################

class stockcomm(object):
    def __init__(self,):
        pass
    def accountInit(self,accountname='account1', initassets=None):
        with mysql.mysql() as db:
            db._cursor.execute("delete from tb_stk_tradelog where accountname = '{}'".format(accountname))
            db._cursor.execute("delete from tb_stk_account where accountname = '{}'".format(accountname))
            db._cursor.execute("insert into tb_stk_account(accountname,withdrawal,assets,initassets) values(?,?,?,?)",(accountname,initassets,initassets,initassets))
    def getWithdrawal(self,accountname=None):
        with mysql.mysql() as db:
            acct = db._cursor.execute("select withdrawal from tb_stk_account where accountname = '{}'".format(accountname)).fetchall()[0]
            return acct[0] if acct else None
    def addCurrStockHold(self):
        pass
    def rmCurrStockHolds(self):
        pass
    def writeTradeLog(self,accountname=None,tdate=None,scode=None,tradetype=None,sprice=None,scount=None):
        with mysql.mysql() as db:
            sql="insert into tb_stk_tradelog(accountname,tdate,scode,tradetype,sprice,samt) values(?,?,?,?,?,?)"
            db._cursor.execute(sql,(accountname,tdate,scode,tradetype,sprice,scount))
    def assetssync(self,accountname=None,commission=None,stockamt=None,tradetype='B'):
        with mysql.mysql() as db:
            op='-' if tradetype == 'B' else '+'
            sql = """update tb_stk_account set 
                     withdrawal = withdrawal - {} %s {},
                     assets = assets-{}
                     where accountname = '{}'"""%(op)
            print (sql.format(round(stockamt*commission,2),stockamt,round(stockamt*commission,2),accountname))
            db._cursor.execute(sql.format(round(stockamt*commission,2),stockamt,round(stockamt*commission,2),accountname))
    def getcommission(self,accountname=None):
        with mysql.mysql() as db:
            sql="select commission from tb_stk_account where accountname = '{}'"
            commission = db._cursor.execute(sql.format(accountname)).fetchall()[0]
            if commission:
                return commission[0] 
            else: 
                return None
    def ordering(self,accountname=None,scode=None,sprice=None,scount=None,stype='B',sdate=None):
        """
        # scode : 股票代码  sz0000001
        # sprice : 股票价格
        # scount : 买入或卖出股票数量 
        # stype : 交易类型 B=buy, S=sell
        # sdate : 交易日期
        """
        withdrawal = self.getWithdrawal(accountname=accountname)
        commission = float(self.getcommission(accountname))
        if stype == 'B':
            #buy
            # 得到帐户可用资金            
            if scount and scount * sprice <= withdrawal:
                #buy successfully                
                self.writeTradeLog(accountname, sdate, scode, 'B', sprice, scount)
                self.assetssync(accountname, commission, sprice*scount,'B')
                return True
            else:
                #failed buy
                return False
        if stype == 'S':
            self.writeTradeLog(accountname, sdate, scode, 'S', sprice, scount)
            self.assetssync(accountname, commission, sprice*scount,'S')

if __name__ == '__main__':
    s = stockcomm()
    s.accountInit(accountname='test1', initassets=1000000)
    #print ( s.getWithdrawal(accountname='test1') )
    #print ( s.getcommission(accountname='test1') )
    #s.writeTradeLog(accountname='test1', tdate='2011-01-01', scode='sz000727', tradetype='B', sprice=10.89, scount=10000)
    #s.assetssync(accountname='test1', commission=0.0005, stockamt=10.89*10700,tradetype='B')
    s.ordering(accountname='test1', scode='sz000727', sprice=10.89, scount=87700, stype='B', sdate='2017-02-08')
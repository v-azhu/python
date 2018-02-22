    
#pyutils.py
# -*- coding: utf-8 -*-
##################################################################
# name     : pyutils
# author   : zhuys
# created  : 2016-07-05
# purpose  : common utilities 
# copyright: copyright(c) zhuyunsheng awen.zhu@hotmail.com 2016-2020
##################################################################
import os
from datetime import datetime
from glob import glob
import cx_Oracle
import pyodbc
import codecs
from HTMLParser import HTMLParser

__all__=['counter','dirWatcher','splitf']
class pydb(object):
    def __init__(self,sid=None):
        self._dbhost = '172.25.200.20' if sid == 'bidb2' else '172.25.200.10'
        self._dbport = '9090'
        self._dbsid  = 'bidb2' if sid == 'bidb2' else 'bidb1'
        #self._dbuser = 'interfaceuser' #'system' 
        #self._dbpass = 'interface_user' #'sys_asdfgh_10'
        self._dbuser = 'hisuser' #'system' 
        self._dbpass = 'pyzxhis_10' #'sys_asdfgh_10'
        os.environ['PATH']= r'C:\Users\zhuys\cygwin64 in;'+os.environ['PATH'] + r';C:\Users\zhuys\instantclient_10_2'
        os.environ['ORACLE_HOME']=r'C:\Users\zhuys\instantclient_10_2'
        os.environ['LD_LIBRARY_PATH']=r'C:\Users\zhuys\instantclient_10_2'
        os.environ['TNS_ADMIN']=r'C:\Users\zhuys\instantclient_10_2\NETWORK\ADMIN'
        #os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.UTF8'
        os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.ZHS16GBK'
    def __enter__(self):
        self._dsn = cx_Oracle.makedsn(self._dbhost,self._dbport,sid=self._dbsid)
        self._conn = cx_Oracle.connect(self._dbuser,self._dbpass,self._dsn)
        self._cursor = self._conn.cursor()
        self._clob = self._cursor.var(cx_Oracle.CLOB)
        self._blob = self._cursor.var(cx_Oracle.BLOB)
        self._str = self._cursor.var(cx_Oracle.STRING)
        return self
    def __exit__(self,type,value,traceback):
        if hasattr(self, "_cursor"): 
            self._cursor.close()
        if hasattr(self, "_conn"): 
            self._conn.commit()
            self._conn.close()
class py157(object):
    def __init__(self):
        self._dbhost = '211.211.8.157'
        self._dbport = '1521'
        self._dbsid  = 'creditdb'
        self._dbuser = 'suidongxiao'
        self._dbpass = 'suidongxiao'
        os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.ZHS16GBK'
    def __enter__(self):
        self._dsn = cx_Oracle.makedsn(self._dbhost,self._dbport,sid=self._dbsid)
        self._conn = cx_Oracle.connect(self._dbuser,self._dbpass,self._dsn)
        self._cursor = self._conn.cursor()
        self._clob = self._cursor.var(cx_Oracle.CLOB)
        self._blob = self._cursor.var(cx_Oracle.BLOB)
        self._str = self._cursor.var(cx_Oracle.STRING)
        return self
    def __exit__(self,type,value,traceback):
        if hasattr(self, "_cursor"): 
            self._cursor.close()
        if hasattr(self, "_conn"): 
            self._conn.commit()
            self._conn.close()            
class mssql(object):
    def __init__(self,server=None):
        self._server = server if server else 'localhost'
    def __enter__(self):
        self._dbconn=pyodbc.connect('DRIVER={SQL SERVER};SERVER='+self._server+';DATABASE=master')
        self._cursor=self._dbconn.cursor()
        return self
    def __exit__(self,type,value,traceback):
        if hasattr(self, "_cursor"): 
            self._cursor.close()
        if hasattr(self, "_conn"):
            self._dbconn.commit()
            self._dbconn.close()
class mysql(object):
    def __init__(self,dsn=None):
        self._dsn = dsn if dsn else "TMDB"
    def __enter__(self):
        self._dbconn=pyodbc.connect("DSN="+self._dsn)
        self._cursor=self._dbconn.cursor()
        return self
    def __exit__(self,type,value,traceback):
        if hasattr(self, "_cursor"): 
            self._cursor.close()
        if hasattr(self, "_conn"):
            self._dbconn.commit()
            self._dbconn.close()               
class MLStripper(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.result = []
    def handle_data(self,d):
        self.result.append(d)
    def get_data(self):
        return ''.join(self.result)
class utils:
    def oraenv32(self):
        os.environ['PATH']= os.environ['PATH'] + r';C:\oracle\product .2.0\client_1\BIN'
        os.environ['ORACLE_HOME']=r'C:\oracle\product .2.0\client_1'
        os.environ['LD_LIBRARY_PATH']=r'C:\oracle\product .2.0\client_1'
        os.environ['TNS_ADMIN']=r'C:\Users\zhuys\instantclient_10_2\NETWORK\ADMIN'
    def oraenv64(self):
        os.environ['PATH']= r'C:\Users\zhuys\cygwin64 in;'+os.environ['PATH'] + r';C:\Users\zhuys\instantclient_10_2'
        os.environ['ORACLE_HOME']=r'C:\Users\zhuys\instantclient_10_2'
        os.environ['LD_LIBRARY_PATH']=r'C:\Users\zhuys\instantclient_10_2'
        os.environ['TNS_ADMIN']=r'C:\Users\zhuys\instantclient_10_2\NETWORK\ADMIN'


    def counter(self,start=0,incrementBy=1,stop=99999999999):
        cnt=start
        while 1:
            yield cnt
            cnt+=incrementBy
            if cnt > stop: raise ValueError, "Overflow the max value of "+str(stop)


    def dirWatcher(self,d):
        maxTimeStamp=datetime.strptime('2016-06-30 09:20:20','%Y-%m-%d %H:%M:%S')
        nextTimeStamp=maxTimeStamp
        nfDic = {"fromDate":None,"fileList":[]}
        while 1:
            nfDic["fromDate"]=nextTimeStamp
            for f in glob(d):
                if os.path.isdir(f): continue
                fts = datetime.fromtimestamp(os.path.getctime(f))
                if fts > maxTimeStamp:
                    nextTimeStamp = fts if fts > nextTimeStamp else nextTimeStamp
                    nfDic["fileList"][0:0]=[{"basename":os.path.basename(f),"fullname":f,"extensionless":os.path.basename(f).split('.')[0],"ctime":fts,"filesize":os.path.getsize(f)}]
            yield nfDic
            maxTimeStamp=nextTimeStamp
            nfDic = {"fromDate":nextTimeStamp,"fileList":[]}
    def splitf(self,srcfile,line=None,filecnt=None,suffix=None):
        suffix = os.path.dirname(srcfile)+'/'+suffix if suffix else srcfile
        llens = 1000 if not line and not filecnt else line         
        with codecs.open(srcfile,'rb',encoding='utf-8') as sf:
            filecontent = sf.readlines()
            totalRows = len(filecontent)
            if not line and filecnt:
                filecnt = 2 if filecnt == 1 else filecnt
                llens = int(round(float(totalRows)/filecnt))
                totalbatches = filecnt
            else:
                totalbatches = (totalRows + llens - 1 ) / llens
            for i in range(totalbatches):
                idxs= i*llens
                idxe = totalRows if not line and filecnt and i+1==totalbatches else idxs+llens
                #print idxs,idxe,filecontent[idxs:idxe]
                with codecs.open(suffix+str(i),'w',encoding='utf-8') as tf:
                    #print filecontent[idxs:idxe]
                    for l in filecontent[idxs:idxe]:tf.write(l)
        return totalRows
    def mergeFiles(self,filePattern=None,outputFile=None):
        with codecs.open(outputFile,'a',encoding='UTF-8') as of:
            for f in glob(filePattern):
                with codecs.open(f,'rb',encoding='UTF-8') as sf:
                    of.write(sf.read())           
                
if __name__== '__main__':
    u = utils()
    lastFile = u.dirWatcher(r'E:\DataIn�606	est\stage\*')    
    #u.split('e:/pic.txt',filecnt=13,suffix='pic')
    u.split('e:/pic.txt',suffix='pic')
    #print 
    #print lastFile.next()["fileList"]
    #for i in range(2):    print lastFile.next()
    #===========================================================================
    # with pyutils.pydb('bidb2') as db:
    #     vOut = db._cursor.var(cx_Oracle.STRING)
    #     db._cursor.execute("
    #     begin 
    #         :out := 'hello world';
    #     end;
    #     ",{'out':vOut})
    #     print vOut.getvalue()
    #===========================================================================
 
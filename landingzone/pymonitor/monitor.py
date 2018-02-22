
#monitor.py
# -*- coding: UTF-8 -*-
###############################################################
# name     : encryption
# author   : zhuys
# created  : 2016-07-05
# purpose  : encrypt/decrypt password
# copyright: copyright(c) zhuyunsheng awen.zhu@hotmail.com 2016
###############################################################
import paramiko,getpass
import encryption
import datetime
import os,re,sys
import lxml.etree as ET
from lxml import _elementpath as _dummy
import cx_Oracle as orcl
from prettytable import PrettyTable
import gzip,decimal
import traceback,exceptions
import codecs
import argparse
import xlwt
import version

class pymon:
    def __init__(self):
        self.rowidx = self.counter()
        self.skey=os.environ['pmonkey']
        self._BaseDir= os.path.split(os.path.abspath(sys.argv[0]))[0]
        os.environ['PATH']= os.environ['PATH'] + r';./oracle'
        os.environ['ORACLE_HOME']=r'./oracle'
        os.environ['LD_LIBRARY_PATH']=r'./oracle'
        os.environ['TNS_ADMIN']=r'./oracle/NETWORK/ADMIN'
        #os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.UTF8'
        os.environ['NLS_LANG']='SIMPLIFIED CHINESE_CHINA.ZHS16GBK'
    def _setVars(self,xpath,typ):
        e=encryption.encryption(self.skey)
        if typ == 'os':
            self._sshHost=self._root.xpath(xpath+'/@ip')[0]
            self._sshPort=self._root.xpath(xpath+'/@sshPort')[0] if self._root.xpath(xpath+'/@sshPort') else 22
            self._sshUser=self._root.xpath(xpath+'/@sshUser')[0]               
            self._sshPass=e.decrypt(self._root.xpath(xpath+'/@sshPass')[0]) if self._root.xpath(xpath+'/@sshPass') else None
        if typ == 'db':
            self._dbHost=self._root.xpath(xpath+'/@ip')[0]
            self._dbPort=self._root.xpath(xpath+'/@dbport')[0] if self._root.xpath(xpath+'/@dbport') else 1521
            self._SID=self._root.xpath(xpath+'/@sid')[0]               
            self._dbUser=self._root.xpath(xpath+'/@dbuser')[0]
            self._dbPass=e.decrypt(self._root.xpath(xpath+'/@dbpass')[0]) if self._root.xpath(xpath+'/@dbpass') else None


    def _entry(self,w):
        for x in range(3):
            entryStr = raw_input("Please entry your "+w)
            if len(entryStr) == 0:
                self._log( "Please entry your "+w )
            else:
                break
        return entryStr
   
    def _log(self,msg,isEncode=False):
        print msg
        if self.outputfile:
            m = '%s%s' % (msg.encode('utf-8'),'') if isEncode else '%s%s' % (msg,'')
            self.fh.write(m)
    def _setval(self,k,v):
        setattr(self.__class__, k,v)
    def osQuery(self,xroot):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            #channel = ssh.invoke_shell()
            for e in xroot.xpath('/monitor/host'):
                if e.tag == 'host':
                    self._log( "Running commands on "+e.attrib['name'] ,True )
                    self._setVars('/monitor/host[@name="'+e.attrib['name']+'"]','os')
                    if e.xpath('./items/item/@toexcel'):self.writexsl(e.attrib['name'].split('	'))
                    if e.attrib['auth'] == 'prompt':
                        ssh.connect(self._sshHost, self._sshPort, self._entry('UserName:'), getpass.getpass('Please entry your password:'))
                    else:
                        ssh.connect(self._sshHost, self._sshPort, self._sshUser, self._sshPass)                    
                    for cmd in e.iter():
                        if 'order' in cmd.keys():
                            self._log( "===> "+cmd.xpath('./@display')[0]+" <===" ,True)
                            stdin,stdout,stderr = ssh.exec_command(cmd.text)
                            for l in stdout.readlines()+ stderr.readlines():
                                if cmd.xpath('./@toexcel'):self.writexsl(l.split('	'))
                                self._log( l.strip(),True )
        except Exception as e:
            self._log( traceback.format_exc(e) )
        finally:
            ssh.close()
    def _dbconn(self):
        _dsn = orcl.makedsn(self._dbHost,self._dbPort,self._SID)
        self._conn = orcl.connect(self._dbUser,self._dbPass,_dsn)
        self._cursor = self._conn.cursor()
        return self
    def _preprocess(self,xnd=None):
        for e in xnd[0].iter():
            if e.tag == 'excel':
                self.xlsx=e.attrib['saveas']
                self.sheet=e.attrib['sheet']
                self.wb=xlwt.Workbook()
                self.sheetHandler = self.wb.add_sheet(self.sheet, cell_overwrite_ok=True)
    def _clearup(self):
        if hasattr(self, "fh"):self.fh.close()
        if hasattr(self, "wb"):self.wb.save(self.xlsx)
    def dbQuery(self,xp): 
        try:
            for e in xp.xpath('/monitor/database'):
                if e.tag == 'database':
                    self._log( "Running commands on "+e.attrib['name'] )
                    if e.xpath('./items/item/@toexcel'):self.writexsl(e.attrib['name'].split('	'))
                    for sql in e.iter():
                        if 'order' in sql.keys():
                            if sql.xpath('./@display'):self._log( "===> "+sql.xpath('./@display')[0]+" <===",True)                            
                            theader = sql.attrib['tabheader'].split()
                            self._setVars('/monitor/database[@name="'+e.attrib['name']+'"]','db')
                            self._dbconn()
                            r = self._cursor.execute(sql.text)
                            ts = PrettyTable(theader)
                            if sql.xpath('./@toexcel'):self.writexsl(theader)
                            for th in theader:
                                ts.align[th]="l"
                            for row in r.fetchall():
                                row = map(lambda x:str(x).decode('GB18030'),row)                                
                                if sql.xpath('./@toexcel'):self.writexsl(row)
                                ts.add_row( row )
                            self._log( ts )

        except Exception as e:
            self._log( traceback.format_exc(e) )
        finally:
            if hasattr(self, "_cursor"):
                self._cursor.close()
            if hasattr(self, "_conn"):
                self._conn.close()
    def counter(self,start=0,incrementBy=1,stop=99999999999):
        cnt=start
        while 1:
            yield cnt
            cnt+=incrementBy
            if cnt > stop: raise ValueError, "Overflow the max value of "+str(stop)
    def writexsl(self,cells):
        ridx = self.rowidx.next()
        if hasattr(self, "sheetHandler"):
            for i,cell in enumerate(cells,start=1):
                self.sheetHandler.write(ridx,i,cell)
    def parseArgs(self):
        try:
            _parser=argparse.ArgumentParser(description="production systems monitor.")
            _parser.add_argument("-c","--config",type=str,required=False,help="Configuration file. mconfig.xml is a default config file which placed where the script is.")
            _parser.add_argument("-o","--output",type=str,required=False,default=None,help="Print out the screen message into a file.")
            _parser.add_argument("-v","--version",action='version',version='%(prog)s '+version.version+' Built by ZhuYunSheng, Copyright(c) 2016-2026 received.',help="version info")
            _pars = _parser.parse_args()
            return _pars
        except Exception as e:
            _parser.parse_args(['--help'])
            raise e

    def pmonmain(self):
        try:
            _args=self.parseArgs()
            self.configfile = _args.config if _args.config else self._BaseDir+'/config/mconfig.xml' 
            self.outputfile = _args.output if _args.output else None
            if self.outputfile: self.fh = codecs.open(self.outputfile,'a')
            tree=ET.parse(self.configfile)
            self._root = tree.getroot()
            self._preprocess(self._root.xpath('/monitor/def'))
            self.dbQuery(self._root)
            self.osQuery(self._root)
        except Exception as e:
            self._log( traceback.format_exc(e) )
        finally:
            self._clearup()            
if __name__ == "__main__":
    pm = pymon()
    pm.pmonmain()

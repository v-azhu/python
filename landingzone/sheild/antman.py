
#antman.py
# -*- coding: utf-8 -*-
import traceback
import pyutils
import argparse
import os,sys,glob,shutil
import subprocess,shlex
from multiprocessing import Process,freeze_support
import json,re
import time,decimal
#######################################################################################
# name     : antman
# author   : zhuys
# created  : 2016-09-25
# purpose  : 064 enterprice data,profile of company, copyright data exp/imp application
# copyright: copyright(c) zhuyunsheng awen.zhu@hotmail.com 2016
#######################################################################################
class antman(object):
    def __init__(self):
        with open(os.path.split(os.path.abspath(sys.argv[0]))[0]+'/aconfig.json','rb') as cfg:
            self.cfgroot = json.load(cfg)
            self._srcdb = self.cfgroot["__configtab__"]["srcdb"]
            self._workdir = self.cfgroot["__configtab__"]["workdir"]
    def _setval(self,k,v):
        setattr(self.__class__, k,v)
    def _setRuntimeVals(self,tab):
        with pyutils.pydb('bidb2') as bidb:
            sql=" select column_name, data_type
                      from all_tab_columns
                     where OWNER = upper(:owner)
                       and TABLE_NAME = upper(:tabname)
                       --and column_name in ('PARTNER_ID','STOCK_TYPE','STOCK_NAME')
                     order by column_id
                "
            self._bvs = bidb._cursor.execute(sql,{"owner":tab.split('.')[0],"tabname":tab.split('.')[1]}).fetchall()
            self._Instmt = "insert into "+tab+"({0})".format(",".join(i[0] for i in self._bvs ))+" values"+"({0})".format(",".join(":b"+str(i) for i in range(len(self._bvs))))
            #self._cols = ",".join( 'substring( i[0] for i in self._bvs )
            self._cols = ",".join( 'substring('+i[0]+',1,1999) '+i[0] if i[1] == 'CLOB' else i[0] for i in self._bvs )
    def createTable(self,tbl=None):
        sql="
        declare
          vTabExists integer;
          vOutput integer;
        begin
            select count(*) into vTabExists
              from all_objects t
             where t.OBJECT_TYPE = 'TABLE'
               and t.OWNER = upper('{owner}')
               and t.OBJECT_NAME = upper('{tab}');
            if vTabExists = 0 then
              :vOutput:=0;
              execute immediate 'create table {ftab} tablespace ts_interface as select * from zhuyunsheng.{seedtab} where 1 = 0';
              execute immediate 'alter table {ftab} nologging';
            else
              :vOutput:=1;
            end if;
        end;
        "
        sql = sql.format(owner=tbl.split('.')[0],tab=tbl.split('.')[1],ftab=tbl,seedtab=re.sub('\d{4,}$','',tbl.split('.')[1]))
        with pyutils.pydb('bidb2') as pydb:
            isTabCreated = pydb._str
            #print sql.format(owner=tbl.split('.')[0],tab=tbl.split('.')[1],ftab=tbl,seedtab=re.sub('\d{4,}$','',tbl.split('.')[1]),vOutput=vOut)            
            pydb._cursor.execute(sql,{'vOutput':isTabCreated})
            return isTabCreated.getvalue()
    def doImport(self,f,batrows=1000):
        try:
            beginTime=time.time()
            with pyutils.mssql() as mssql:
                with pyutils.pydb('bidb2') as db:
                    with open(f,'rb') as fil:
                        lines=[x.strip() for x in fil.readlines() ]
                        totalrownum = len(lines)
                        totalpage = (totalrownum + batrows - 1 ) / batrows
                        for i in range(totalpage):
                            idxs= i*batrows
                            idxe=idxs+batrows
                            batch=lines[idxs:idxe]
                            pids = "'{0}'".format("','".join(batch))
                            if self._tab.lower() == 't_annual_administration_license' :self._cols = self._cols.replace('ANNUAL_ADMIN_LICENSE_ID','ANNUAL_ADMINISTRATION_LICENSE_ID')
                            stmt="select "+self._cols+" from "+self._srcdb+".."+self._tab+" where "+self._pk+" in( {partner_id} )".format(partner_id=pids)
                            boundvalues=[]
                            for r in mssql._cursor.execute(stmt).fetchall():
                                for i,v in enumerate(self._bvs):
                                    if v[1] in('VARCHAR2','CLOB'): 
                                        r[i] = r[i].encode('GB18030') if r[i] else None
                                    elif v[1] in('NUMBER','INTEGER'): 
                                        r[i] = r[i] if r[i] else 0
                                    else:
                                        r[i] = r[i] if r[i] else None
                                boundvalues.append(r)
                            db._cursor.prepare(self._Instmt)
                            db._cursor.executemany(None,boundvalues)
                            db._conn.commit()
            #to avoid devision by zero.
            totalTime= 1 if int(time.time()-beginTime) == 0 else int(time.time()-beginTime)
            print "file=%s, ImportedRows=%d, TotalTime=%s sec, processAvgSpeed=%d rows/sec." % (f,totalrownum,totalTime,int(totalrownum/totalTime))
        except Exception as e:
            print 'processfile=%s,lastrow=%s' % (f,idxs)
            print traceback.format_exc(e)
    def tabPKExp(self,cmd):
        args = shlex.split(cmd)
        p = subprocess.Popen(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        _stdout,_stderr = p.communicate(input=None)
        print _stdout,_stderr
    def parseArgs(self):
        try:
            _parser=argparse.ArgumentParser(description="064 company data export/import application.")
            _parser.add_argument("-t","--table",type=str,required=True,help="The table to transfer data")
            _parser.add_argument("-a","--all",action='store_true',default=False,help="Do all actions for given table")
            _parser.add_argument("-s","--split",action='store_true',default=False,help="split file to m parts")
            _parser.add_argument("-e","--exportid",action='store_true',default=False,help="export primary key from table")
            _parser.add_argument("-i","--impdat",action='store_true',default=False,help="import data into target by extract data from source.")
            _parser.add_argument("-v","--version",action='version',version='%(prog)s 1.9.0 Built by zhuys, Copyright(c) 2016-2026 received.',help="version info")
            _pars = _parser.parse_args()
            return _pars
        except Exception as e:
            _parser.parse_args(['--help'])
            raise e
    def _getData(self,html):
        mlhandler=pyutils.MLStripper()
        mlhandler.feed(html)
        return mlhandler.get_data()
    def corpProfile(self,f,batrows=1000):
        with open(f,'rb') as js:self.comp = json.load(js)
        with pyutils.pydb('bidb2') as db:
            sql="insert into "+self._tgttab+" values(interfaceuser.seq_t_corp_intro_id.nextval,:1,:2)"
            boundvalues=[]
            rows=self.comp["RECORDS"]
            totalrownum = len(rows)
            totalpage = (totalrownum + batrows - 1 ) / batrows
            for i in range(totalpage):
                idxs= i*batrows
                idxe=idxs+batrows
                batch=rows[idxs:idxe]
                boundvalues=[]
                for r in batch:
                    name=self._getData(r["Name"]).encode('GB18030') if self._getData(r["Name"]) else ''
                    content=self._getData(r["Content"]).encode('GB18030') if self._getData(r["Content"]) else ''
                    if len(content) > 2000:
                        lobsql="insert into "+self._tgttab+" values(interfaceuser.seq_t_corp_intro_id.nextval,:name,:content)"
                        db._cursor.setinputsizes(name=db._clob,content=db._clob)
                        db._cursor.execute(lobsql,{"name":name,"content":content})
                        db._conn.commit()
                    else:
                        boundvalues.append((name,content))                        
                db._cursor.prepare(sql)
                db._cursor.executemany(None,boundvalues)
                db._conn.commit()
    def copyrightInfo(self,f,batrows=1000):
        try:
            fileds=[u"类别",u"分类号",u"版本号",u"登记号",u"作品名称",u"登记日期",u"作品著作权人",u"创作完成日期",u"首次发布日期",u"发布日期",u"软件全称",u"软件简称",u"登记批准日期",u"软件著作权人"]
            sql="insert into "+self._tgttab+" values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16)"
            #sql="insert into zhuyunsheng.tb_copyright_info0928 values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16)"
            with open(f,'rb') as cf: lines=cf.readlines()
            with pyutils.pydb('bidb2') as db:
                totalrownum = len(lines)
                totalpage = (totalrownum + batrows - 1 ) / batrows
                for i in range(totalpage):
                    idxs= i*batrows
                    idxe=idxs+batrows
                    batch=lines[idxs:idxe]
                    boundvalues=[]
                    for l in batch:
                        if len(l)<20:continue
                        row=[]
                        r=l.split('|')
                        if len(r)>3:
                            fixedRow=r[:2]
                            fixedRow.append('|'.join(r[2:]))
                            r=fixedRow
                        cls = re.findall('"(.*)"',r[1])[0] if r[1] else ''
                        row.append(re.findall('"(.*)"',r[0])[0] if r[0] else -1)
                        #row.append(re.findall('"(.*)"',r[1])[0] if r[1] else '')
                        row.append(cls.decode('utf-8').encode('GB18030'))
                        # we are using unicode pattern matches chinese character here.
                        js =  re.findall(u'"(.*)"',r[2],re.M)[0] if r[2] else ''
                        js = js.replace('""','"')
                        jst = json.loads(js)
                        for filed in fileds:
                            if filed in jst.keys():
                                row.append(jst[filed].encode('GB18030'))
                            else:
                                row.append('')
                        boundvalues.append(row)
                    db._cursor.prepare(sql)
                    db._cursor.executemany(None,boundvalues)
                    db._conn.commit()
        except Exception as e:
            print traceback.format_exc(e)
    def main(self):
        args = self.parseArgs()
        u = pyutils.utils()
        aBeginTime=time.time()
        self._tab = args.table
        if self._tab not in self.cfgroot.keys():
            print "The table not configed yet! supported tables : %s" % map(lambda x:x if x!= '__configtab__' else '', self.cfgroot.keys())
            sys.exit()
        self._tgttab = self.cfgroot[args.table]['tgt']
        self._fname = self.cfgroot[args.table]['funname']
        if self._tab not in ('tb_copyright_info','t_corp_intro'):
            self._setRuntimeVals(self._tgttab)
            self._pk = self.cfgroot[args.table]['pk']
            if args.exportid or args.all:
                print "starting export pk from %s.%s" % (self._srcdb,args.table)
                argstr = 'bcp "select '+self.cfgroot[args.table]["pk"]+' from '+self._srcdb+'..'+args.table+'" queryout '+self._workdir+'/'+args.table+' -c -q -t "|" -T'
                self.tabPKExp(argstr)
        if self._tab not in ('t_corp_intro'):
            if args.split or args.all:
                print "starting split files to 10 more parts."
                if self._tab == 'tb_copyright_info':
                    shutil.copy(self.cfgroot[args.table]['srcfile'], self._workdir)
                    self._totalRows = u.splitf(srcfile=self._workdir+'/'+os.path.basename(self.cfgroot[args.table]['srcfile']), filecnt=20,suffix=self.cfgroot[args.table]["shortname"])
                else:
                    self._totalRows = u.splitf(srcfile=self._workdir+'/'+args.table, filecnt=20,suffix=self.cfgroot[args.table]["shortname"])
        else:
            if args.split or args.all: 
                for f in glob.glob(self.cfgroot[args.table]['srcfile']+'*.json'):
                    shutil.copy(f, self._workdir)
        if args.impdat or args.all:
            try:
                ffunc = getattr(self, self._fname)
            except:
                raise NotImplementedError("Class %s does not implement %s"%(self.__class__.__name__,self._fname))
            print "starting import data into target in pll."
            allfiles = glob.glob(self._workdir+'/'+self.cfgroot[args.table]["shortname"]+'*')            
            for f in allfiles:
                p = Process(target=ffunc,args=(f,))
                p.start()
                print "processor=%s with file=%s"%(p.name,f)
            p.join()
            totalTime = time.time()-aBeginTime
            if hasattr(self, "_totalRows"):print "all done. TakeTimes=%d sec. AvgSpeed=%d rows/sec."%(totalTime,int(self._totalRows/totalTime))
if __name__ == "__main__":
    freeze_support()
    ins = antman()
    #ins.main()
    print ins.createTable('interfaceuser.t_annual_invest_info1610')
    # for %i in (t_annual_asset t_annual_basic_info t_annual_branch t_annual_change t_annual_employee t_annual_invest_info t_annual_partner t_annual_report t_annual_stock_change t_annual_website t_branch t_change t_company t_employee t_opexception t_partner t_annual_administration_license) do c:\Users\zhuys\Python27\python.exe antman.py -t %i -a


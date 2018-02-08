
 # -*- coding: GBK -*-
 import os,re
 import subprocess,shlex
 import traceback,pyutils
 from datetime import datetime,timedelta
 import threading
 from prettytable import PrettyTable
 
 class ade():
     def __init__(self):
         self._config = r'C:\Users\zhuys\workspace\dataloader\config.json'
     def _callcmd(self,cmd):
         p = subprocess.Popen(shlex.split(cmd),stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
         (_stdout, _stderr) = p.communicate(input=None)
         print _stdout
         print _stderr
         print p.returncode
     def hisTabGen(self,tab):
         with pyutils.pydb('bidb2') as db:
             tgtOwner = "HISUSER"            
             #srcOwner = tab.split('.')[0].encode('utf-8')
             srcOwner = db._cursor.execute('select srctab1 from zhuyunsheng.vmetadatads t where t.tgtttab = :tab',tab=tab).fetchone()[0].split('.')[0]
             #srcTab = tab.split('.')[1]
             srcTab = tab
             tgtTab = srcTab
             sql = "select zhuyunsheng.PKG_UTILITIES.f_TabGen(:srcOwner,:srcTab,:tgtOwner,:tgtTab,:dropIfExists) from dual"
             ddl = db._cursor.execute(sql,{"srcOwner":srcOwner,"srcTab":srcTab,"tgtOwner":tgtOwner,"tgtTab":tgtTab,"dropIfExists":"Y"}).fetchone()[0].read()
         print ddl
         ddlfile = str(srcTab)+'.sql'
         self.touch(ddlfile)
         with open(r'./sql/tables/'+ddlfile,'w') as fo:
             fo.write(ddl)
         u = pyutils.utils()
         u.oraenv32()
         cmd = os.system(r"echo exit | sqlplus hisuser/pyzxhis_10@bidb2 @C:\Users\zhuys\workspace\dataloader\sql	ables/"+ddlfile)
         if cmd != 0:print cmd
     def hiTrigGen(self,tab):
         tgtOwner = 'HISUSER'
         with pyutils.pydb('bidb2') as db:
             srcOwner = tab.split('.')[0].encode('utf-8')
             srcTab = tab.split('.')[1]
             tgtTab = srcTab
             sql = "select zhuyunsheng.PKG_UTILITIES.f_TriggerGen(:srcOwner,:srcTab,:tgtOwner,:tgtTab) from dual"        
             db._cursor.execute(sql,{"srcOwner":srcOwner,"srcTab":srcTab,"tgtOwner":tgtOwner,"tgtTab":tgtTab})
             ddl = db._cursor.fetchone()[0].read()
             print ddl
         #=======================================================================
         #     ddlfile = str(srcOwner)+'_'+str(srcTab)+'.sql'
         #     self.touch(ddlfile)
         #     with open(r'./sql/triggers/'+ddlfile,'w') as fo:
         #         fo.write(ddl+'/exit;')
         # u = pyutils.utils()
         # u.oraenv32()
         # cmd = os.system(r"echo exit | sqlplus hisuser/pyzxhis_10@bidb2 @C:\Users\zhuys\workspace\dataloader\sql	riggers/"+ddlfile)
         # if cmd != 0:print cmd
         #=======================================================================
         
     def pyTrigGen(self,tab,bk='ID'):
         trigTemp="""WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK;
 create or replace trigger PYDATAUSER.TRIG_{trigName}
   after insert or update or delete on HISUSER.{tab} for each row
   /*
   CopyRight(c) All right saved by pycredit inc.,
   Author  :  zhuys
   Date    :  {timestamp}
   Purpose :  Trigger on table HISUSER.{tab} to keeping data in sync after history data load. .
   ChangeList :  {timestamp} init checkin.
   */
 declare
   vColList PYDATAUSER.{tab}%ROWTYPE;
 begin
 {declaration}
   if INSERTING then      
       {bkdecision} 
       insert into pydatauser.{tab}(
 {collist})
 {vallist});
   elsif UPDATING then  
       delete from pydatauser.{tab} where id = :old.ID;
       insert into pydatauser.{tab}(
 {collist})
 {vallist});      
   else 
       delete from pydatauser.{tab} where id = :old.ID;
   end if;
 exception 
   when others then 
    insert into tb_trig_tracker(tid,trigname,tgtname,srcname,errdate,errmsg) values(seq_trig_tracker_tid.nextval,'PYDATAUSER.TRIG_{trigName}'
    ,'PYDATAUSER.{tab}','HISUSER.{tab}',sysdate,dbms_utility.format_error_stack || dbms_utility.format_error_backtrace ); 
 end;
 /
         """
         sqlWeighing = """
             select  nvl(decode(column_name,
                         'CREATETIME',decode(zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER',:tab,'CREATTIME'),1,'CREATTIME',decode(zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER',:tab,'BUILDTIME'),1,'BUILDTIME')),
                         'MODIFYTIME',decode(zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER',:tab,column_name),0,'MODITYTIME',column_name),
                         column_name),column_name),count(*) over() cnt from (
              select column_name,decode(column_name,'MODIFYTIME',80,'CREATETIME',60,'RECIEVETIME',40,20)+decode(nullable,'N',100,0) weighing
                from all_tab_columns
               where owner = 'PYDATAUSER'
                 and table_name = :tab
                 and DATA_TYPE in ('DATE','TIMESTAMP(3)','TIMESTAMP(6)')
                 and column_name <> 'INFODATE'
                 and rownum < 3
                 ) order by 2 desc
         """
         sql = """
           select column_name,
                  nvl(decode(column_name,
                         'CREATETIME',decode(zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER',:tab,'CREATTIME'),1,'CREATTIME',decode(zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER',:tab,'BUILDTIME'),1,'BUILDTIME')),
                         'MODIFYTIME',decode(zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER',:tab,column_name),0,'MODITYTIME',column_name),
                         column_name),column_name) hiscolname, 
                 max(length(column_name)) over() + 2 width,
                 sign(column_id - count(*) over()) isLast,
                 length(column_name) collen,
                 column_id
            from all_tab_columns
           where owner = 'PYDATAUSER'
             and table_name = :tab
             order by column_id
         """
         declaration,collist,vallist,bkdecision,stmtend,bkdecisionend = ['' for x in range(6)]
         if bk != 'ID':
             bkdecision = '-- check to see if the data exists by business key. deleting before inserting if exists.'
             bkdecision += '      delete from pydatauser.'+tab+'        where '
             for i,b in enumerate(bk.split(','),start=1):
                 if i == len(bk.split(',')):stmtend=';'
                 bkdecision += b + ' = vColList.'+b+stmtend+'' if i == 1 else '         {0}'.format('and '+ b + ' = vColList.'+b+stmtend)            
				 width = 0 
         with pyutils.pydb('bidb2') as db:
             weighing = db._cursor.execute(sqlWeighing,tab=tab).fetchall()
             if len(weighing) == 1:
                 infodate = 'nvl(:new.'+weighing[0][0]+',sysdate)'
                 infodateInit = 'nvl('+weighing[0][0]+',sysdate)'
             elif len(weighing) == 2:
                 infodate = 'nvl(nvl(:new.'+weighing[0][0]+',:new.'+weighing[1][0]+'),sysdate)'
                 infodateInit = 'nvl(nvl('+weighing[0][0]+','+weighing[1][0]+'),sysdate)'
             else:
                 infodate = 'sysdate'
                 infodateInit = 'sysdate'
             clms = db._cursor.execute(sql,tab=tab).fetchall()
             for clm in clms:
                 if clm[0] == 'INFODATE':
                     declaration += '  vColList.{0:<{width}}'.format(clm[0],width=clm[2])+':= '+infodate+';'
                 else:
                     if clm[0] == 'NAME':
                         declaration += '  vColList.{0:<{width}}'.format(clm[0],width=clm[2])+':= to_single_byte(trim(:new.{0}));'.format(clm[1])+''
                     elif clm[0] == 'DOCUMENTNO':
                         declaration += '  vColList.{0:<{width}}'.format(clm[0],width=clm[2])+':= pybaseuser.utils.Doc15To18(:new.{0});'.format(clm[1])+''
                     else:
                         declaration += '  vColList.{0:<{width}}'.format(clm[0],width=clm[2])+':= :new.{0};'.format(clm[1])+''
                 width = int(len(tab)+30+clm[4])
                 collist+= '{0:>{width}}'.format(clm[0],width=width) if clm[3] == 0 else '{0:>{width}},'.format(clm[0],width=width)
                 width = int(len(tab)+39+clm[4])
                 if clm[5] == 1:
                     vallist+= '{0:>{width}},'.format('values (vColList.'+clm[0],width=width)
                 else:
                     vallist+= '{0:>{width}}'.format('vColList.'+clm[0],width=width) if clm[3] == 0 else '{0:>{width}},'.format('vColList.'+clm[0],width=width)
         #d = {"tab":tab,"trigName":'None',"timestamp":None,"declaration":None,"iai":None,"diau":None,"delete":None}
         ddltrig = trigTemp.format(tab=tab,trigName=tab[3:28],timestamp=str(datetime.today())[:19],declaration=declaration,collist=collist,vallist=vallist,bkdecision=bkdecision)
         print ddltrig
         #print 'pydatauser.trig_'+tab[3:28]
         #=======================================================================
         # with open(r'./sql/triggers/trig_'+tab[3:]+'.sql','w') as fo:
         #     fo.write(ddltrig)
         # u = pyutils.utils()
         # u.oraenv32()
         # cmd = os.system(r"echo exit | sqlplus hisuser/pyzxhis_10@bidb2 @C:\Users\zhuys\workspace\dataloader\sql	riggers/trig_"+tab[3:]+".sql")
         # if cmd != 0:print cmd
         #=======================================================================
     def pytabGen(self,tab):
         ddlt,ddlp,ddli,ddlc,ddlph,ts=[ '' for v in range(6) ]
         with pyutils.pydb('bidb2') as db:
             sql =  """
                 select row_number() over(order by inv.column_id) rn, 
                        inv.COLUMN_NAME,
                        inv.data_type,
                        inv.data_scale,
                        inv.data_length,
                        inv.nullable,
                        inv.data_precision,
                        inv.data_default,
                        count(*) over() cnt,
                        nvl(TABLESPACE_NAME,'TS_PYDATA') tablespace_name 
                 from (
                 select t.COLUMN_ID,
                        t.COLUMN_NAME,
                        t.DATA_TYPE,
                        t.DATA_SCALE,
                        t.DATA_LENGTH,
                        t.NULLABLE,
                        t.DATA_PRECISION,
                        ZHUYUNSHENG.pkg_utilities.f_getDefVal('HISUSER',:tab,t.COLUMN_NAME) data_default,
                        nvl(ts.TABLESPACE_NAME,(select max(tablespace_name) from all_tab_partitions where  table_owner = 'HISUSER' and table_name = :tab)) TABLESPACE_NAME
                   from all_tab_columns t,all_tables ts
                  where t.OWNER = ts.OWNER
                    and t.TABLE_NAME = ts.TABLE_NAME
                    and t.OWNER = 'HISUSER'
                    and t.TABLE_NAME = :tab
                    --and t.column_name not in ('REFUNITID','REFUSERID','REFPERSONID')
                    and t.column_name not in ('REFID','REFUNITID','REFUSERID','REFPERSONID','DATASOURCE')
                 union
                 select 999999 column_id,'INFODATE' COLUMN_NAME, 'DATE' DATA_TYPE, null DATA_SCALE, null DATA_LENGTH, 'N',null DATA_PRECISION, 'SYSDATE' DATA_DEFAULT, '' TABLESPACE_NAME
                   from dual where 0 = (select zhuyunsheng.pkg_utilities.f_ColVerify('HISUSER', :tab, 'INFODATE')from dual)
                 ) inv
             """
             ddlt += "WHENEVER SQLERROR EXIT SQL.SQLCODE ROLLBACK"
             ddlt += "DROP TABLE PYDATAUSER."+tab+";"
             ddlt += "CREATE TABLE PYDATAUSER."+tab+" ("
             for row in db._cursor.execute(sql,{"tab":tab}).fetchall():
                 if row[0] == 1:ts = row[9].replace('HIS','PYDATA') 
                 datatyp= ' INTEGER' if row[2] == 'NUMBER' and row[4] == 22 and row[3] == 0 else ' '+row[2]                
                 if row[2] == 'NUMBER' and row[4] == 22:
                     datalen = '' 
                 elif row[2] in ('DATE','TIMESTAMP(3)','TIMESTAMP(6)','CLOB','BLOB','LONG'):
                     datalen = ''
                 else:
                     datalen = '({0})'.format(row[4])
                 dftval = ''{0}''.format(row[7]) if row[2] in ('VARCHAR2','CHAR') else row[7]
                 dftexp=' DEFAULT '+ row[7].strip('') if row[7] else ''
                 nullable= ' NOT NULL' if row[5] == 'N' else ''
                 rowend = '' if row[8] == row[0] else ','
                 colDef = row[1]+ datatyp + datalen + dftexp + nullable + rowend 
                 ddlt += colDef + ''
             ddlt += ")"
             sql = """
                 select c.column_name,
                        b.partitioning_type,
                        a.partition_name,
                        a.high_value,
                        a.high_value_length,
                        a.partition_position,
                        a.tablespace_name,
                        count(*) over() cnt
                   from all_tab_partitions a, all_part_tables b, all_part_key_columns c
                  where a.table_owner = b.owner
                    and a.table_name = b.table_name
                    and a.table_owner = c.owner
                    and a.table_name = c.name
                    and a.table_owner = 'HISUSER'
                    and a.table_name = :tab
             """
             prtn = db._cursor.execute(sql,{"tab":tab}).fetchall()
             for row in prtn:
                 ddlp += "partition "+row[2]+' values less than ' + '({0})'.format(row[3]) +' tablespace '+row[6].replace('HIS','PYDATA') + ['' if row[5] == row[7] else ','][0]
             if len(prtn) > 0:
                 ddlph = "partition by "+row[1]+'({0})'.format(row[0]) + '({0})'.format(ddlp)+';'
             else:
                 ddlph = "tablespace "+ts+";" 
             sql = """
                 select b.index_name,
                       cast(wm_concat(b.COLUMN_NAME) as varchar2(100)) colist,
                       nvl(replace(tablespace_name,'_HIS_','_PYDATA_'),'TS_PYDATA') tablespace_name
                  from all_indexes a, all_ind_columns b
                 where a.TABLE_OWNER = b.TABLE_OWNER
                   and a.TABLE_NAME = b.TABLE_NAME
                   and a.INDEX_NAME = b.INDEX_NAME
                   and a.table_owner in ( 'HISUSER','PYDATAUSER')
                   and a.table_name = :tab
                   and a.uniqueness = 'NONUNIQUE'
                   and a.status = 'VALID'
                   --and b.column_name not in ('ID','REFUNITID','REFUSERID','REFPERSONID')
                   and b.column_name not in ('REFID','REFUNITID','REFUSERID','REFPERSONID','DATASOURCE')
                 group by b.index_name,tablespace_name
                 union
                 select 'IDX_'||substr(t.TABLE_NAME,4,26)||'_'||decode(t.COLUMN_NAME,'PERSONID','PSNID','CORPID','CPID') index_name,
                        t.COLUMN_NAME,(select nvl(v.pyts,v.hists)||'_IDX' from zhuyunsheng.vmetadatads v where v.tgtttab = :tab) tablespace_name
                   from all_tab_columns t
                  where t.OWNER = 'HISUSER'
                    and t.table_name = :tab
                    and t.COLUMN_NAME in ('PERSONID', 'CORPID')
             """
             idex = db._cursor.execute(sql,{"tab":tab}).fetchall()
             for idx in idex:
                 ddli += "create index PYDATAUSER."+idx[0]+ " on PYDATAUSER."+tab+"({0})".format(idx[1])+" tablespace "+idx[2].replace('HIS','PYDATA')+";"
             idxname = "IDX_"+tab[5:28]+"_ID" if len(tab) > 23 else "IDX_"+tab[3:]+"_ID"
             if idex:
                 ddli += "create index PYDATAUSER."+idxname+" on PYDATAUSER."+tab+" (ID) tablespace "+idx[2].replace('HIS','PYDATA')+";"
             else:
                 ddli += "create index PYDATAUSER."+idxname+" on PYDATAUSER."+tab+" (ID) tablespace ts_pydata_base_idx;"
             sql = """
               select column_name,comments
                 from all_col_comments t
                where t.OWNER = 'HISUSER'
                  and t.TABLE_NAME = :tab
                  and t.COMMENTS is not null
                  --and t.column_name not in ('REFUNITID','REFUSERID','REFPERSONID')
                  and t.column_name not in ('REFID','REFUNITID','REFUSERID','REFPERSONID','DATASOURCE')
             """
             for c in db._cursor.execute(sql,{"tab":tab}).fetchall():
                 cmts=c[1]
                 ddlc += "comment on table PYDATAUSER."+tab+" is 'created by zhuys on "+str(datetime.today())+" '; "
                 ddlc += "comment on column PYDATAUSER."+tab+"."+c[0]+" is '{0}'".format(cmts) +";"
         #print ddlt+ddlph+ddli+ddl
         with open(r'./sql/tables/'+tab+'.sql','w') as fo:
             fo.write(ddlt+ddlph+ddli+ddlc)
         u = pyutils.utils()
         u.oraenv32()
         cmd = os.system(r"echo exit | sqlplus hisuser/pyzxhis_10@bidb2 @C:\Users\zhuys\workspace\dataloader\sql	ables/"+tab+".sql")
         if cmd != 0:print cmd
     def pyDupIdentify(self,tab):
         sql = """
          select a.column_name,
                 a.data_type,
                 a.data_scale,
                 a.data_length,
                 a.nullable,
                 a.data_precision,
                 a.data_default,
                 (
                 zhuyunsheng.pkg_utilities.f_isPK('PYCORPUSER',:tab,a.column_name)+
                 zhuyunsheng.pkg_utilities.f_isPK('SERVICEUSER',:tab,a.column_name)+
                 zhuyunsheng.pkg_utilities.f_isPK('CREDITUSER',:tab,a.column_name)+
                 zhuyunsheng.pkg_utilities.f_isPK('HISUSER',:tab,a.column_name)+
                 zhuyunsheng.pkg_utilities.f_isPK('PYDATAUSER',:tab,a.column_name)
                 ) isIndexed
            from all_tab_columns a
           where a.owner = 'PYDATAUSER'
             and a.table_name = :tab
             and a.data_type not in ('CLOB','BLOB','BFILE','LONG')
             and a.data_length < 300
             and a.column_name not in ('ID', 'INFODATE')
             order by a.column_id
         """
         cols=[]
         weighing=0
         grpby,bk,cmts=['' for v in range(3)]
         with pyutils.pydb('bidb2') as db:
             for t in db._cursor.execute(sql,{"tab":tab}).fetchall():
                 if t[1] not in ('DATE,TIMESTAMP(3),TIMESTAMP(6)'):weighing+=10
                 if re.findall('ID$|NAME$|CODE$|NO$',t[0],re.I):weighing+=20
                 if t[4] == 'N':weighing+=50
                 if t[6]:weighing+=30
                 if t[7]>0:weighing+=40
                 cols.append((t[0],weighing))
                 weighing=0
             for col in sorted(cols,key=lambda tup:tup[1],reverse=True):                
                 grpby += col[0] if len(grpby)<2 else ','+col[0]
                 uniqueRow="select count(*) from (select {grpby},count(*) from pydatauser.{tab} group by {grpby} having count(*) > 1)"
                 duprow=db._cursor.execute(uniqueRow.format(tab=tab,grpby=grpby)).fetchone()[0]
                 cmts += "table: "+tab+", groupby: "+grpby+", rows: "+str(duprow)+""
                 if duprow==0:
                     bk = grpby
                     break
             print tab,bk,cmts
             db._cursor.execute('update zhuyunsheng.tb_metadata_ds set bussinesskeys = :bk,comments = :cmts where tgtttab = :tab',{"tab":tab,"bk":bk,"cmts":cmts})
             db._conn.commit()
     
     def pyDupAnalyze(self):
         with pyutils.pydb('bidb2') as db:
             for k in db._cursor.execute("select v.tgtttab,v.bussinesskeys from zhuyunsheng.tb_metadata_ds v where v.topydata = 'Y' and v.bussinesskeys is not null").fetchall():
                 sql = """
                 select * from (
                     select id,count(*) over(partition by {collist}) cnt from hisuser.{tab}
                     ) where cnt > 1 order by cnt desc
                 """
                 ids=''
                 res = db._cursor.execute(sql.format(tab=k[0],collist=k[1])).fetchmany(30)
                 if not res:continue
                 for i,id in enumerate(res,start=1):
                     if i == id[1]:
                         break
                     else:
                         ids+=str(id[0]) if i == 1 else ','+str(id[0])
                 sql = """
                 create table zhuyunsheng.{tab} as select * from hisuser.{tab} where id in ({ids})
                 """
                 print sql.format(tab=k[0],ids=ids)
                 db._cursor.execute(sql.format(tab=k[0],ids=ids))
     def pyDupRun(self):
         with pyutils.pydb('bidb2') as db:
             for t in db._cursor.execute("select tgtttab from zhuyunsheng.vmetadatads v where v.topydata = 'Y' and v.srcCount = 1 and v.bussinesskeys is null").fetchall():
                 if 'QUERYLOG' in t[0]:continue
                 self.pyDupIdentify(t[0])
     def pyinit(self):
         sql = """
         select v.id,v.tgtttab,v.bussinesskeys from zhuyunsheng.vmetadatads v where v.topydata = 'Y' and v.bussinesskeys is not null
         """
         rmDup="delete from pydatauser.{tab} where id not in (select max(id) from pydatauser.{tab} group by {bk})"        
         with pyutils.pydb('bidb2') as db:
             for t in db._cursor.execute(sql).fetchall():
                 print rmDup.format(tab=t[1],bk=t[2])
                 db._cursor.execute(rmDup.format(tab=t[1],bk=t[2]))
                 db._conn.commit()
     def cmplTrig(self,tab):
         sql="""
         declare
             vOutput varchar2(4000);
         begin
             for i in (select a.OWNER||'.'||a.TRIGGER_NAME trgname,a.TABLE_OWNER,a.TABLE_NAME,a.STATUS ast,b.status bst,b.CREATED
                       from all_triggers a, all_objects b
                      where a.OWNER = b.OWNER
                        and a.TRIGGER_NAME = b.OBJECT_NAME
                        and b.OBJECT_TYPE = 'TRIGGER'
                        and a.TABLE_NAME = '{tab}') loop
                 vOutput:=vOutput||chr(13)||'The trigger '||i.trgname||' with status '||i.ast||' and '||i.bst;
                 if i.ast <> 'ENABLED' or i.bst <> 'VALID' then
                    execute immediate 'alter trigger '||i.trgname||' compile';
                    execute immediate 'alter trigger '||i.trgname||' enable';
                    vOutput:=vOutput||chr(13)||'Compile and enable trigger : '||i.trgname;
                 end if;
             end loop;
             :out:=vOutput;
         end;
         """
         with pyutils.pydb('bidb2') as db:
             db._cursor.execute(sql.format(tab=tab),{'out':db._str})
             db._conn.commit()
             print db._str.getvalue()
             print "*"*20+""
     def hiSync(self,tab):
         sql="""
         select owner,
                tabname table_name,
                owner || '.' || tabname fullname,
                decode(OWNER,'CREDITUSER',1,'SERVICEUSER',3,'PYCORPUSER',4,'VIPUSER',5,2) DS
           from (select regexp_substr(inv, '[^.]+', 1, 1, 'i') owner,
                        regexp_substr(inv, '[^.]+', 1, 2, 'i') tabName
                   from (select regexp_substr((select t.srctab from zhuyunsheng.vmetadatads t where t.tgtttab = '{tab}'),'[^,]+',1,level,'i') as inv
                           from dual
                         connect by level < 50)
                  where inv is not null)
         """
         self.cmplTrig(tab)
         with pyutils.pydb('bidb2') as db:
             pt = PrettyTable(['TableName','RowCount'])
             for r in db._cursor.execute(sql.format(tab=tab)).fetchall():
                 srowcnt = db._cursor.execute(r'select count(*) from {tab}'.format(tab=r[2])).fetchone()[0]
                 trowcnt = db._cursor.execute(r'select count(*) from hisuser.{tab} where datasource = {ds}'.format(tab=r[1],ds=r[3])).fetchone()[0]
                 pt.add_row([r[2],srowcnt])
                 pt.add_row([r[1]+'({0})'.format('datasource='+str(r[3])),trowcnt])
                 if srowcnt != trowcnt and srowcnt > 1000000:
                     self.catchup(r[2],r[3])
                 elif srowcnt != trowcnt:
                     sql="""
                     begin
                         begin
                             execute immediate 'drop table zhuyunsheng.aaa';
                             exception
                               when others then
                                 null;
                         end;
                         execute immediate 'alter table pydatauser.{tab} nologging';
                         execute immediate 'alter table hisuser.{tab} nologging';
                         execute immediate 'alter table {fullname} nologging';
                         execute immediate 'create table zhuyunsheng.aaa as select * from {fullname}';
                         execute immediate 'delete from hisuser.{tab} where datasource = {ds}';
                         execute immediate 'truncate table {fullname}';
                         execute immediate 'insert into {fullname} select * from zhuyunsheng.aaa';
                         execute immediate 'alter table pydatauser.{tab} logging';
                         execute immediate 'alter table hisuser.{tab} logging';
                         execute immediate 'alter table {fullname} logging';
                         commit;
                     end;
                     """
                     #print sql.format(tab=r[1],fullname=r[2],ds=r[3])
                     db._cursor.execute(sql.format(tab=r[1],fullname=r[2],ds=r[3]))
                     db._conn.commit()
                     print "The data get synced : "+r[2]
             print pt
     def catchup(self,tab,ds):
         sql="""
         begin
             execute immediate 'alter table pydatauser.{tab} logging';
             execute immediate 'alter table hisuser.{tab} logging';
             execute immediate 'alter table {fulltab} logging'; 
         end;
         """
         print sql.format(tab=tab.split('.')[1],fulltab=tab,ds=ds)
         with pyutils.pydb('bidb2') as db:
             db._cursor.execute(sql.format(tab=tab.split('.')[1],fulltab=tab,ds=ds))
             db._conn.commit()
         threads=[]
         for t in self.stageData(tab,ds):
             threads.append(threading.Thread(target=self.instUpstream,args=(t,tab,)))
         for th in threads:
             th.start()
         th.join()    
     def instUpstream(self,src,tgt):
         sql="insert into {tgt} select * from zhuyunsheng.{src}"
         print sql.format(src=src,tgt=tgt)
         with pyutils.pydb('bidb2') as db:
             db._cursor.execute(sql.format(src=src,tgt=tgt))
             db._conn.commit()
     def stageData(self,fulltab,ds):
         batch=20
         tablist=[]
         threads=[]
         for i in range(batch):
             tab=fulltab.split('.')[1][3:]+'_'+str(i)
             tablist.append(tab)
             threads.append(threading.Thread(target=self.createStag,args=(fulltab,batch,i,)))
         for th in threads:
             th.start()
         th.join()
         sql="""
         begin
             execute immediate 'alter table pydatauser.{tab} nologging';
             execute immediate 'alter table hisuser.{tab} nologging';
             execute immediate 'alter table {fulltab} nologging';
             execute immediate 'delete from hisuser.{tab} where datasource = {ds}';
             execute immediate 'truncate table {fulltab}';            
         end;
         """
         print sql.format(tab=fulltab.split('.')[1],fulltab=fulltab,ds=ds)
         with pyutils.pydb('bidb2') as db:
             db._cursor.execute(sql.format(tab=fulltab.split('.')[1],fulltab=fulltab,ds=ds))
             db._conn.commit()
         return tablist
     def createStag(self,fulltab,batch,subbch):
         tab=fulltab.split('.')[1][3:]+'_'+str(subbch)
         sql="""
         begin
             begin
                 execute immediate 'drop table zhuyunsheng.{tab}';
                 exception 
                   when others then
                     null;
             end;
             execute immediate 'create table zhuyunsheng.{tab} as select * from {fulltab} where mod(ID,{batch}) = {subbch}';
         end;
         """
         print sql.format(tab=tab,fulltab=fulltab,batch=batch,subbch=subbch)
         with pyutils.pydb('bidb2') as db:
             db._cursor.execute(sql.format(tab=tab,fulltab=fulltab,batch=batch,subbch=subbch))
             db._conn.commit()
     def verifyAll(self,tab):
         sql="""
         declare
             vCnt integer:=0;
             vSQL clob;
             vSSTMT varchar2(4000);
             vTSTMT varchar2(4000);
             vOutput clob:='{{RowCount:{{';
         begin
             for i in (select owner,tabname,owner||'.'||tabname fullname, decode(owner,'CREDITUSER',1,'SERVICEUSER',3,'PYCORPUSER',4,'VIPUSER',5,2) DS,
                             sign(rownum - count(*) over()) flg from (
                         select regexp_substr(tab, '[^.]+', 1, 1, 'i') owner,
                                regexp_substr(tab, '[^.]+', 1, 2, 'i') tabName
                           from (select regexp_substr((select t.srctab
                                                        from zhuyunsheng.vmetadatads t
                                                       where t.tgtttab = '{tbl}'),
                                                      '[^,]+', 1, level, 'i') as tab
                                   from dual connect by level < 50)
                          where tab is not null
                         )) loop
                 execute immediate 'select count(*) from '||i.fullname  into vCnt;                
                 vOutput:=vOutput||''''||i.fullname||''':'||vCnt||',';
                 execute immediate 'select count(*) from hisuser.'||i.tabname||' where datasource = '||i.DS into vCnt;
                 vOutput:=vOutput||''''||'HISUSER-'||i.DS||'.'||i.tabname||''':'||vCnt||',';
             end loop;
             execute immediate 'select count(*) from pydatauser.{tbl}' into vCnt;
             -- Verify triggers
             vOutput:=vOutput||''''||'PYDATAUSER.{tbl}'||''':'||vCnt||'}},Triggers:[';            
             for trg in (select a.OWNER||'.'||a.TRIGGER_NAME trgname,
                                a.TABLE_OWNER,a.TABLE_NAME,a.STATUS ast,b.status bst,
                                to_char(b.CREATED,'yyyy-mm-dd hh24:mi:ss') CREATED,
                                to_char(b.LAST_DDL_TIME,'yyyy-mm-dd hh24:mi:ss') LAST_DDL_TIME,
                                sign(rownum - count(*) over()) flg
                           from all_triggers a, all_objects b,(select regexp_substr(tab, '[^.]+', 1, 1, 'i') owner,
                                regexp_substr(tab, '[^.]+', 1, 2, 'i') tabName
                           from (select regexp_substr((select t.srctab
                                                        from zhuyunsheng.vmetadatads t
                                                       where t.tgtttab = '{tbl}'),
                                                      '[^,]+', 1, level, 'i') as tab
                                   from dual connect by level < 50)
                          where tab is not null) c
                          where a.OWNER = b.OWNER
                            and a.TRIGGER_NAME = b.OBJECT_NAME
                            and a.TABLE_OWNER = c.owner(+)
                            and a.TABLE_NAME = c.tabname(+)
                            and b.OBJECT_TYPE = 'TRIGGER'
                            and a.TABLE_NAME = '{tbl}') loop
                 vOutput:=vOutput||'('||trg.trgname||','||trg.TABLE_OWNER||','||trg.table_name||','||trg.ast||','||trg.bst||','||trg.created||','||trg.last_ddl_time||case trg.flg when -1 then '),' else ')]' end; 
             end loop;
             -- verify records
             vOutput:=vOutput||',{{';
             for t in (select owner || '.' || tabname fullname,tabname,sign(rownum-count(*) over()) flg
               from (select regexp_substr(tab, '[^.]+', 1, 1, 'i') owner,
                            regexp_substr(tab, '[^.]+', 1, 2, 'i') tabName
                       from (select regexp_substr((select t.srctab
                                                    from zhuyunsheng.vmetadatads t
                                                   where t.tgtttab = '{tbl}'),
                                                  '[^,]+', 1, level, 'i') as tab
                               from dual
                             connect by level < 50)
                      where tab is not null)) loop
                 for r in (select COLUMN_NAME fcn,decode(COLUMN_NAME,'ID','REFID','UNITID','REFUNITID','PERSONID','REFPERSONID','USERID','REFUSERID',COLUMN_NAME) hcn,sign(rownum-count(*) over()) flg from (
                             select t.COLUMN_NAME,zhuyunsheng.pkg_utilities.f_ColVerify('SERVICEUSER','TB_MICRO_PERSON',t.column_name) isUpstreamExists
                               from all_tab_columns t
                              where t.TABLE_NAME = t.tabname
                                and t.owner = 'HISUSER'
                                order by t.COLUMN_ID
                             ) where isUpstreamExists > 0
                             ) loop
                     vSSTMT:=vSSTMT||r.fcn||case r.flg when -1 then ',' else null end;
                     vTSTMT:=vTSTMT||r.hcn||case r.flg when -1 then ',' else null end;
                 end loop;
                 vOutput:=vOutput||'''SQL_'||t.tabname||''':''select '||vSSTMT||' from '||t.fullname||' minus select '||vTSTMT||' from HISUSER.{tbl}'''||case t.flg when -1 then ',' end;
             end loop;
             vOutput:=vOutput||'}}}}';
             :out:=vOutput;
         end;
         """
         #print sql.format(tbl=tab)
         with pyutils.pydb('bidb2') as db:
             db._cursor.execute(sql.format(tbl=tab),{'out':db._clob})
             db._conn.commit()
             print db._clob.getvalue()
     def adRun(self,tab):
         try:
             #self.hisTabGen(tab)
             with pyutils.pydb('bidb2') as db:
                 upstreamtab = 'select srctab from zhuyunsheng.vmetadatads where tgtttab = :tab'
                 for t in db._cursor.execute(upstreamtab,tab=tab).fetchone():
                     for s in t.split(','):
                         self.hiTrigGen(s)
             #self.pytabGen(tab)
             self.pyTrigGen(tab)
             self.hiSync(tab)
         except Exception as e:
             print "An error occurred during processing table = "+tab
             print traceback.format_exc(e)
     def touch(self,f):
         with open(f,'w'):
             os.utime(f,None)
     def tmp(self):
         sql="""
             declare
               vSrcCnt integer;
               vTgtCnt integer;
               vOut varchar2(1000):='';
             begin
                 select count(refid) into vSrcCnt from HISUSER.TB_REPORT_RECORDBAT where receivetime >= to_date('{beginDate}','yyyy-mm-dd hh24:mi:ss') and receivetime < to_date('{endDate}','yyyy-mm-dd hh24:mi:ss');
                 select count(refid) into vTgtCnt from PYDATAUSER.TB_REPORT_RECORDBAT where receivetime >= to_date('{beginDate}','yyyy-mm-dd hh24:mi:ss') and receivetime < to_date('{endDate}','yyyy-mm-dd hh24:mi:ss') and datasource = 1;
                 if vSrcCnt > vTgtCnt then
                   --execute immediate 'truncate table zhuyunsheng.aaa';
                   --execute immediate 'truncate table zhuyunsheng.bbb';
                   --execute immediate 'truncate table zhuyunsheng.ccc';
                   execute immediate 'insert into PYDATAUSER.TB_REPORT_RECORDBAT select * from ('
                     ||' select * from HISUSER.TB_REPORT_RECORDBAT t ' 
                     ||' where t.receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'') '
                     ||' and t.receivetime < to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                     ||'minus '
                     ||' select * from PYDATAUSER.TB_REPORT_RECORDBAT t' 
                     ||' where t.receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                     ||' and t.receivetime < to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                                     ||')';
                   execute immediate 'delete from PYDATAUSER.TB_REPORT_RECORDBAT where receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                     ||' and receivetime <  to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                     ||' and id not in ('
                     ||' select max(id)'
                     ||' from PYDATAUSER.TB_REPORT_RECORDBAT t'
                     ||' where t.receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                     ||' and t.receivetime <  to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'')'
                     ||' group by refid, datasource)';
                     
                   --execute immediate 'insert into zhuyunsheng.bbb select refid from HISUSER.TB_REPORT_RECORDBAT where receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'') and receivetime < to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'') and datasource = 1';
                   --execute immediate 'delete from zhuyunsheng.aaa t1 where exists (select * from zhuyunsheng.bbb t2 where t1.id = t2.refid)';
                   --execute immediate 'insert into zhuyunsheng.ccc select * from CREDITUSER.TB_REPORT_RECORDBAT where id in (select * from zhuyunsheng.aaa)';
                   --execute immediate 'delete from PYCORPUSER.TB_REPORT_RECORDBAT where id in (select * from zhuyunsheng.aaa)';
                   --execute immediate 'insert into PYCORPUSER.TB_REPORT_RECORDBAT select * from zhuyunsheng.ccc';
                   --execute immediate 'insert into zhuyunsheng.TB_REPORT_RECORDBAT select * from zhuyunsheng.ccc';
                   commit; 
                   vOut:=vOut||' SrcTab='||vSrcCnt||', TgtTab='||vTgtCnt||', RowDiff='||(vSrcCnt-vTgtCnt)||', EffectedRows='||SQL%ROWCOUNT;
                 elsif vSrcCnt < vTgtCnt then
                   execute immediate 'delete from hisuser.TB_REPORT_RECORDBAT a where a.receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'') and a.receivetime < to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'') and not exists (select 1 from CREDITUSER.TB_REPORT_RECORDBAT b where b.receivetime >= to_date(''{beginDate}'',''yyyy-mm-dd hh24:mi:ss'') and b.receivetime < to_date(''{endDate}'',''yyyy-mm-dd hh24:mi:ss'') and a.refid = b.id ) and a.datasource = 1';
                   vOut:=vOut||' SrcTab='||vSrcCnt||', TgtTab='||vTgtCnt||', RowDiff='||(vSrcCnt-vTgtCnt)||', EffectedRows='||SQL%ROWCOUNT;
                 else
                   vOut:=vOut||' SrcTab='||vSrcCnt||', TgtTab='||vTgtCnt||', RowDiff='||(vSrcCnt-vTgtCnt)||', EffectedRows=0';
                 end if;
                 :out:=vOut;
             end;
         """
         beginDate = datetime.strptime('2015-12-03','%Y-%m-%d')
         endDate = beginDate + timedelta(1)
         with pyutils.pydb('bidb2') as db:
             while True:
                 if beginDate >= datetime.strptime('2016-11-21','%Y-%m-%d'):break
                 #print sql.format(beginDate=beginDate,endDate=endDate)
                 #db._cursor.execute(sql,{"beginDate":beginDate,"endDate":endDate,"out":db._str})
                 db._cursor.execute(sql.format(beginDate=beginDate,endDate=endDate),{"out":db._str})
                 db._conn.commit()
                 outmsg=db._str.getvalue()
                 ddf = re.findall('RowDiff=(\d+)',outmsg)[0] 
                 if int(ddf) <> 0:
                     print "beginDate=%s endDate=%s %s" % (beginDate,endDate,outmsg)
                 beginDate = endDate
                 endDate = endDate + timedelta(1)
                 
     def runPll(self):
         try:
             threads=[]
             tl = ['REPORT_SUBQUERY_RECORD_'+str(i) for i in range(20)]
             for t in tl:
                 threads.append(threading.Thread(target=self.tmp,args=(t,)))
             for th in threads:
                 th.start()
             th.join()
         except Exception as e:
             print traceback.format_exc(e)
 if __name__ == "__main__":
     pd = ade()
     #pd.tmp()
     #pd.ademain()
     #tl = ['TB_REPORT_RECORDBAT_OFFLINE']
     #for t in tl:
         #pd.adRun(t)
         #pd.hiSync(t)
         #pd.cmplTrig(t)
         #pd.hisTabGen(t)
     #pd.runPll()
     #pd.hiSync('TB_NET_CORP_CONTACT_ADDR')
     #pd.verifyAll('TB_MICRO_LOAN_STATUS')
     #===========================================================================
     # pd.adRun('TB_EDU_QUERYLOG')
     # pd.pyDupIdentify('TB_PATENT_BASE')
     # pd.pyDupRun()
     # pd.pyDupAnalyze()
     pd.pyTrigGen('TB_MICRO_LOAN_STATUS')
     # pd.hiSync('TB_NET_CORP_CONTACT_ADDR')
     # pd.hisTabGen('TB_REPORT_STAT_MON')
     # pd.pytabGen('TB_EDU_QUERYLOG')
     # pd.pyinit()
     #===========================================================================


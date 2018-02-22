
#blackwidow.py
import pyutils
import os,time,glob
import json,codecs
import multiprocessing
import traceback
#######################################################################################
# name     : blackwidow
# author   : zhuys
# created  : 2016-09-25
# purpose  : operation behavior data parser/loader
# copyright: copyright(c) zhuyunsheng awen.zhu@hotmail.com 2016
#######################################################################################
def opBehavior(f,batrows=1000):
    fields=['_id','uid','platformType','otherValue','netType','deviceId','className','inputIDs','osVersion','shareType','endTime','text','eventId','_class','startTime','model','monitorId','fragmentName','sharePlatformType','createDate']
    with codecs.open(f,'rb',encoding='UTF8') as jsn:
        with pyutils.py157() as db:
            sql="insert into TB_OP_BEHAVIOR_1611f values(:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16,:17,:18,:19,:20)"
            lines=[x.strip() for x in jsn.readlines() ]
            totalrownum = len(lines)
            totalpage = (totalrownum + batrows - 1 ) / batrows
            for i in range(totalpage):
                idxs= i*batrows
                idxe=idxs+batrows
                batch=lines[idxs:idxe]
                boundvalues=[]
                for l in batch:
                    infroot = json.loads(l)
                    row=[]
                    for k in fields:
                        if k in infroot.keys():
                            if k=='_id':
                                row.append(infroot[k]['$oid'])
                            else: 
                                row.append(infroot[k].encode('gb18030') if infroot[k] else '')
                        else:
                            row.append('')
                    boundvalues.append(row)
                db._cursor.prepare(sql)
                db._cursor.executemany(None,boundvalues)
                db._conn.commit()
def main(fl):
    try:
        beginDate=time.time()
        u = pyutils.utils()
        u.splitf(srcfile=fl, filecnt=10,suffix='oph')
        allfiles = glob.glob(os.path.split(os.path.abspath(fl))[0]+'/oph*')
        for f in allfiles:
            p = multiprocessing.Process(target=opBehavior,args=(f,))
            p.start()
            print "processor=%s with file=%s"%(p.name,f)
        p.join()
        print "all done, Total Time=%d sec.,"%int(time.time()-beginDate)
    except Exception as e:
        traceback.format_exc(e)
        print "error file="%f
if __name__ == "__main__":
    main('E:/DataIn/201611/behavior/cs20160930_8.json')
    #opBehavior('E:/DataIn/201611/behavior/11')

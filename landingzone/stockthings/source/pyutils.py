# -*- coding:utf-8 -*-
###############################################################################
# name      : pyutils.py
# author    : awen.zhu@hotmail.com
# created   : 2017-10-10
# purpose   : python use defined utils
# python version : 3.6
# os : windows 10 64bit
# copyright : copyright (c) zhuyunsheng awen.zhu@hotmail.com all rights received  
################################################################################
import os
import csv
import random
from datetime import datetime,timedelta
import win32com.client
import requests
from multiprocessing import Process

class utils(object):
    def readInChunks(self,fileObj,chunklines=10240000):
        while True:
            data = fileObj.readlines(chunklines)
            if not data:break
            yield data
    def csv2json(self,f):
        js={}
        csvdata = csv.reader(f,delimiter='\t',quotechar='"')
        print ( csvdata.next() )
    def idgen(self,areacode=None,birthday=None,sex=None,num=5):
        """
        generates chinese identify card number by given conditions.
        areacode : 6-digital number to identify the area
        birthday : 8-digital number to identify birthday, yyyymmdd
        sex      : male or female, m=male,f=famale
        num      : generates idcode counts.
        """
        areacode = areacode if areacode else '110000'        
        startdate=datetime.strptime('19500101','%Y%m%d')
        enddate=datetime.strptime('20010101','%Y%m%d')
        ddelta=enddate-startdate
        birthday = birthday if birthday else datetime.strftime( startdate + timedelta(random.randint(1,ddelta.days)) ,'%Y%m%d')
        weigth = [ 7,9,10,5,8,4,2,1,6,3,7,9,10,5,8,4,2 ]
        valid= [ '1','0','X','9','8','7','6','5','4','3','2' ]
        if sex == 'F':
            tmplist = random.sample(list ( filter(lambda y:y%2==0, [x for x in range(1000)] ) ),num)
        elif sex == 'M':
            tmplist = random.sample(list ( filter(lambda y:y%2!=0, [x for x in range(1000)] ) ),num)
        else:
            tmplist = random.sample([x for x in range(1000)] ,num)             
        for i in tmplist:
            first17 = areacode+birthday+'%03d'%i 
            # identify the validate code 
            s,m = 0,0
            for v in range(len(first17)):s = s + ( int(first17[v]) * weigth[v] )
            m = s % 11
            idcode = first17+valid[m]
            yield (idcode)
    def createfile(self,fullname):
        if not os.path.exists(os.path.abspath(fullname)):
            open(os.path.abspath(fullname),'w').close()
            return True
        else:
            return False
    def pdf2docx(self,infile=None,outfile=None):
        """sample covert pdf file to docx by using win32API since this way might be more better than other similar tools.
        Parameters:
        -----------
        infile : input file, format: pdf with full path and name. if a dir given, it will covert dir's all pdf file 
        outfile : output file, format: docx with same name as infile, if path not given, it will be saved input file's path.
        
        Return Values:
        --------------
        True if all done.
        False if some error occured.
        """
        try:
            # parsing parameters... let's do it later.
            word = win32com.client.Dispatch("Word.Application")
            word.visible = 0
            wb = word.Documents.Open(infile)
            wb.SaveAs2(outfile, FileFormat=16) 
            # For details of FileFormat visit : https://docs.microsoft.com/en-us/dotnet/api/microsoft.office.interop.word.wdsaveformat?view=word-pia
            r = True
        except:
            r = False
            raise
        finally:
            wb.Close()
            word.Quit()
            return r
    def writedisk(self,filename=None,startof=0,content=None):        
        with open(os.path.abspath(filename),'rb+') as fh:
            fh.seek(startof)
            fh.write(content)
    def download(self,url=None,headers=None,filename=None,threadcnt=1):
        try:
            filename = os.path.basename(requests.utils.urlparse(url).path) if filename is None else filename
            res = requests.get(url,headers=headers)
            if 'Content-Length' not in res.headers.keys():
                self.downloadinchuck(url, headers, filename)
                return True
            else:
                if int(res.headers['Content-Length']) < 10 or res.headers['Content-Type'] == 'text/html':
                    print(res.text)
                    return False
            if res.status_code > 300:return False
            size = int(res.headers['Content-Length'])
            offset = round(size/threadcnt)
            steps = size//offset + 1 if size/offset > size//offset else size//offset
            startof = 0
            endof = offset if size > offset else size
            self.createfile(filename)
            for i in range(steps):
                headers['range'] = 'bytes={s:d}-{e:d}'
                headers['range'] = headers['range'].format(s=startof,e=endof) if steps > 1 else 'bytes=0-'
                res = requests.get(url,headers=headers)
                print ("status_code=%s"%(res.status_code))
                print ("start writing piece %s of %s,block=(%s,%s)/%s"%(i,steps,startof,endof,size))
                p=Process(target=self.writedisk,args=(filename,startof,res.content))
                p.start()
                startof = endof + 1
                endof = endof+offset if endof + offset < size else size
            p.join()
            return True if p.exitcode == 0 else False
        except:
            raise
    def downloadinchuck(self,url=None,headers=None,filename=None):
        try:
            filename = os.path.basename(requests.utils.urlparse(url).path) if filename is None else filename
            self.createfile(filename)
            res = requests.get(url,headers=headers)
            startof = 0
            for c in res.iter_content(1024):
                self.writedisk(filename,startof,c)
                startof += 1024
        except:
            raise        
    def datadic2sql(self,excel=None,sheet=None):
        """
        Conver a data diction from excel to sql script 
        """
        import pandas
        pd = pandas.read_excel(io=excel, sheet_name=sheet)
        gpd = pd.groupby( ['tabname'] )
        print ( gpd.head() )
if __name__ == "__main__":
    u = utils()
    #### test
    ids = u.idgen(areacode='410101',birthday='20010201',sex='M',num=100)
    #for i in range(100):print(next(ids))
    #u.csv2json('e:/1.txt')
    #u.datadic2sql(excel='d:/Book1.xlsx', sheet='Sheet1')

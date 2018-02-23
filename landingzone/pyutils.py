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
import csv
import random
from datetime import datetime,timedelta
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
if __name__ == "__main__":
    u = utils()
    #### test
    ids = u.idgen(birthday='20000101',num=100)
    for i in range(10):print(next(ids))
    #u.csv2json('e:/1.txt')
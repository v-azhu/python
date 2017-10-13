# -*- coding:utf-8 -*-
###############################################################################
# name      : pyutils.py
# author    : carl_zys@163.com
# created   : 2017-10-10
# purpose   : python use defined utils
# copyright : copyright (c) zhuyunsheng carl_zys@163.com all rights received  
################################################################################
import csv
import datetime
class utils(object):
    def readInChunks(self,fileObj,chunklines=10240000):
        while True:
            data = fileObj.readlines(chunklines)
            if not data:break
            yield data
    def csv2json(self,f):
        js={}
        csvdata = csv.reader(f,delimiter='\t',quotechar='"')
        print csvdata.next()

if __name__ == "__main__":
    u = utils()
    #u.csv2json('e:/1.txt')
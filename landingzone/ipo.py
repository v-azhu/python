# -*- coding: gb18030 -*- 
import urllib.request
from bs4 import BeautifulSoup
import sys,io

__author__='carl_zys@163.com'
# change default output encoding as gb18030 to avoid encoding error.

class ipo(object):
    def getIPOInfo(self):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030')
        with open('ipohistdata.txt','rb') as f:stocks = f.readlines()
        for i,stock in enumerate(stocks):
            if i < 1:
                stock = stock.decode().rstrip()
                url = """http://data.eastmoney.com/xg/xg/detail/{0}.html?tr_zqh=1""".format(stock)
                print ( "processing with url = %s"%url )
                data = urllib.request.urlopen(url).read()
                soup = BeautifulSoup(data,'html.parser')
                tables=soup.findAll('table', attrs={'class':'tab1'})
                print ( data )
    def IPOparser(self):
        with open('tmp/002864.txt','rb') as f:
            soup = BeautifulSoup(f.read().decode('gb18030'),'html.parser')
            tables=soup.findAll('table')
            i=0
            tags=['��Ʊ����','��Ʊ���','�깺����','���м۸�Ԫ���ɣ�','���Ϸ�������','������������','���Ϸ�������(��)','������������(��)','�ܷ����������ɣ�','�깺��������(��)',
                  'ĩ\"��\"λ��']
            for tb in tables:
                for tr in tb.findAll('tr'):
                    tds = tr.findAll('td')
                    for tag in tags:
                        while i < len(tds):
                            if tds[i].text.strip() == tag:
                                print ( tag,tds[i+1].text.strip() )
                                i+=1
                            i+=1
                        i=0
if __name__ == "__main__":
    ipo = ipo()
    ipo.getIPOInfo()
    #ipo.IPOparser()
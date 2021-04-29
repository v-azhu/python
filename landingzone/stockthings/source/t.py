
# -*- coding:utf-8 -*-
import os
import requests
import pyutils
import datetime as dt

if __name__ == "__main__":
    u = pyutils.utils()
    #url=r'http://www.sse.com.cn/disclosure/listedinfo/announcement/c/2020-10-31/600008_20201031_6.pdf'
    url = r'https://upos-sz-mirrorhw.bilivideo.com/upgcxcode/57/69/183316957/183316957-1-16.mp4?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1609317267&gen=playurl&os=hwbv&oi=2028275689&trid=c672462916ad4830a6fd86727e9d183ah&platform=html5&upsig=494e03232d3f851f0c60e5a5ef58ead0&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,platform&mid=0&logo=80000000'
    #url='http://disc.static.szse.cn/download/disc/disk02/finalpage/2020-12-03/8ee689f2-7dbe-4b6a-883d-5e23d3e6254b.PDF'
    #url='http://disc.static.szse.cn/download/disc/disk02/finalpage/2020-12-25/d3f937b4-7f23-406e-bd76-936e3348b37e.PDF'
    headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'Accept-Encoding': 'gzip, deflate'
               }
    #d = u.downloadinchuck(url, headers, None)
    #print ("done")
    #print (d)
    #res = requests.get(url,headers)
    #print ("headers=%s"%res.headers)
    #p = requests.utils.urlparse(url)
    #print (p.path,os.path.basename(p.path))
    start_date = dt.datetime.strftime(dt.datetime.today(),'%Y-%m-%d')
    print(start_date,type(start_date))
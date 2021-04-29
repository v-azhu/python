# -*- coding:utf-8 -*-
import os
import requests
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from multiprocessing import Process,freeze_support
import traceback

def getBVideo():
    try:
        #url=r'https://www.bilibili.com/video/BV15t411Q7Nb?from=search&seid=2436501992092999894'
        #url=r'https://www.bilibili.com/video/BV1Nt411y78P/?spm_id_from=333.788.recommend_more_video.0'
        #url=r'https://www.bilibili.com/video/BV1bt411m7JB/?spm_id_from=333.788.recommend_more_video.0'
        url = r'https://www.bilibili.com/video/BV1DT4y1G7Vs?from=search&seid=4016994637172204084'
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        mobile_emulation = {'deviceName': 'iPhone 6 Plus'}
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        browser = webdriver.Chrome(options=options)
        browser.maximize_window()
        browser.get(url)
        allvideos = browser.find_elements_by_xpath('//div[@class="m-video-part-new"]/ul/li')
        if len(allvideos) == 0:
            v = browser.find_element_by_tag_name('video')
            text = browser.find_elements_by_xpath('//*[@id="app"]/div/div/div[4]/div[1]/div[1]/h1')[0].text
            src = v.get_attribute('src')
            print ('text=%s,src=%s'%(text,src))
            download(v.text,src)
        else:
            wait = WebDriverWait(browser, 10)
            for v in allvideos:
                v.click()
                wait.until(lambda x:x.find_element_by_tag_name('video'))
                src = browser.find_element_by_tag_name('video').get_attribute('src')
                print ('text=%s,src=%s'%(v.text,src))
                download(v.text,src)
    except:
        raise
    finally:
        browser.quit()

def writedisk(filename=None,startof=None,content=None):
    if not os.path.exists(os.path.abspath(filename)):
        open(os.path.abspath(filename),'w').close()
    with open(os.path.abspath(filename),'rb+') as fh:
        fh.seek(startof)
        fh.write(content)
def download(filename,url):
    try:
        #url=r'https://upos-sz-mirrorhw.bilivideo.com/upgcxcode/36/63/65726336/65726336-1-6.mp4?e=ig8euxZM2rNcNbdlhoNvNC8BqJIzNbfq9rVEuxTEnE8L5F6VnEsSTx0vkX8fqJeYTj_lta53NCM=&uipk=5&nbs=1&deadline=1608725475&gen=playurl&os=hwbv&oi=2028275482&trid=a4e0645e8c384fe282fbfa0212df233ch&platform=html5&upsig=4dc8eafee9b4090973515897af3c52ce&uparams=e,uipk,nbs,deadline,gen,os,oi,trid,platform&mid=0&logo=80000000'
        #url='https://pics2.baidu.com/feed/d01373f082025aafeaa219e373bd6363024f1ad9.jpeg?token=a06dc962eb9e6936b6b2d3251ed7ed3c&s=BE0A7223D2AC4D1D98B8FDC30100A091'
        #url='https://www.bilibili.com'
        #filename,url=getBVideo()
        cookie = "finger=-53268994; _uuid=B9A88712-7A95-B30B-96D1-E2174661616478901infoc; buvid3=FCC11A7E-CC96-41EC-8547-583B0759BCD7143098infoc; CURRENT_FNVAL=80; blackside_state=1; rpdid=|(k|k)k~lY~l0J'uY|~YYlR|l; bsource=search_google; sid=jxvwzp08"
        headers = {'user-agent': 'user-agent: Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Mobile Safari/537.36',
                   'authority': 'upos-sz-mirrorhw.bilivideo.com',
                   'accept': '*/*',
                   'accept-encoding': 'identity;q=1, *;q=0',
                   'accept-language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
                   'dnt': '1',
                   'origin': 'https://m.bilibili.com',
                   'range': 'bytes=0-',
                   'referer': 'https://m.bilibili.com/',
                   'sec-fetch-dest': 'video',
                   'sec-fetch-mode': 'cors',
                   'sec-fetch-site': 'cross',
                   'Cookie':cookie
                   }
        res = requests.get(url,headers=headers)
        size = int(res.headers['Content-Length'])
        print ("size=%s,Content-Length=%s"%(size,res.headers['Content-Length']))
        threadcnt = 5
        offset = round(size/threadcnt)
        steps = size//offset + 1 if size/offset > size//offset else size//offset
        startof = 0
        endof = offset if size > offset else size
        for i in (range(steps)):
            headers['range'] = 'bytes={s:d}-{e:d}'
            headers['range'] = headers['range'].format(s=startof,e=endof)
            res = requests.get(url,headers=headers)
            print ("status_code=%s"%(res.status_code))
            print ("start writing piece %s of %s,block=(%s,%s)"%(i,steps,startof,endof))
            #print ("content=%s"%res.content)
            writedisk(filename+'.mp4',startof,res.content)
            p=Process(target=writedisk,args=(filename+'.mp4',startof,res.content))
            p.start()
            startof = endof + 1
            endof = endof+offset if endof + offset < size else size
        p.join()
            #print (res.cookies)
    except Exception as e:
        print (traceback.format_exc(e))
    
if __name__ == "__main__":    
    freeze_support()
    getBVideo()
    #download()
    
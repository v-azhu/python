# -*- coding:utf-8 -*-
from lxml import html,etree
import time,os
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import datetime as dt

import requests

def isElementPresent(browser,by, value):
    try:
        browser.find_element(by=by, value=value)
    except NoSuchElementException as e:
        return False
    return True

def getFruitAppleInfo():
    try:
        chrome_options = webdriver.ChromeOptions()
        # add dev model to avoid identified by taobao
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        #chrome_options.add_argument('--headless')
        #chrome_options.add_argument('--window-size=1920x1080')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_experimental_option("detach", True)
        browser = webdriver.Chrome(options=chrome_options)
        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",})
        browser.maximize_window()
        url=r'https://s.taobao.com/search?q=%E8%8B%B9%E6%9E%9C&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_20210112&ie=utf8&cps=yes&cat=50108542&sort=sale-desc'
        browser.get(url)
        WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.ID,'fm-login-id'))).send_keys(os.environ['usr'])
        WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.ID,'fm-login-password'))).send_keys(os.environ['pwd'])
        loginbutton = browser.find_element_by_xpath('//div[@class="fm-btn"]/button')
        loginbutton.click()
        time.sleep(30)
#         while True:
#             if isElementPresent(browser, By.XPATH,"//div[@class='site-nav-user']"):
#                 print("login successfully.")
#                 break
#             else:
#                 #iframe = browser.find_element_by_id('baxia-dialog-content')
#                 #browser.switch_to.frame(iframe)
#                 dragbutton = WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.ID,'nc_1_n1z')))
#                 action = ActionChains(browser)
#                 action.click_and_hold(dragbutton).perform()
#                 action.move_by_offset(258, 0).perform()
#                 action.reset_actions()
        WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.CLASS_NAME,'items')))
        totalpages = ''.join(list(filter(str.isdigit,browser.find_element_by_class_name('total').text)))
        #totalpages = 3 if int(totalpages) > 3 else int(totalpages)
        totalpages = int(totalpages)
        extractdate = dt.datetime.strftime(dt.datetime.today(),'%Y-%m-%d')
        for p in range(2,totalpages,1):
            items = browser.find_elements_by_xpath('//*[@id="mainsrp-itemlist"]/div/div/div[1]/*')
            for item in items:
                nid = item.find_element_by_xpath('./div[1]/div/div[1]/a').get_attribute('trace-nid')
                title = item.find_element_by_xpath('./div[1]/div/div[1]/a/img').get_attribute('alt')
                price = item.find_element_by_xpath('./div[1]/div/div[1]/a').get_attribute('trace-price')
                itemurl = item.find_element_by_xpath('./div[1]/div/div[1]/a').get_attribute('href')
                dealcnt =  item.find_element_by_class_name('deal-cnt').text
                shopname = item.find_element_by_xpath('./div[2]/div[3]/div[1]/a/span[2]').text
                shoplocation = item.find_element_by_class_name('location').text
                shopurl = item.find_element_by_xpath('./div[2]/div[3]/div[1]/a').get_attribute('href')
                print("page=%s,nid=%s,title=%s,price=%s,dealcnt=%s,shopname=%s,shoplocation=%s"%(p,nid,title,price,dealcnt,shopname,shoplocation))
                with open("taobaodata.csv","a+") as f:
                    f.write('"%s","%s","%s","%s","%s","%s","%s","%s","%s","%s"\n'%(extractdate,p-1,nid,title,price,itemurl,dealcnt,shopname,shoplocation,shopurl))
            browser.find_element_by_link_text('%s'%p).click()
            time.sleep(3)
    except:
        raise
    finally:
        pass
        #browser.close()
if __name__ == "__main__":
#     doc = docx.Document(r'300507.docx')
#     tables = doc.tables
#     tbl = tables[8]
#     for r in range(len(tbl.rows)):
#         v = ''
#         lastvalue=''
#         for l in range(len(tbl.columns)):
#             if lastvalue != tbl.cell(r,l).text and len(tbl.cell(r,l).text.strip())>0 :
#                 v += tbl.cell(r,l).text
#             lastvalue = tbl.cell(r,l).text
#         print (r,v)
    getFruitAppleInfo()
    
#     button = driver.find_element_by_xpath(’//*[@id=“slider2”]/div/div[2]’) # 找到“蓝色滑块”
# action = ActionChains(driver) # 实例化一个action对象
# action.click_and_hold(button).perform() # perform()用来执行ActionChains中存储的行为
# action.move_by_offset(400, 0).perform()
# action.reset_actions()
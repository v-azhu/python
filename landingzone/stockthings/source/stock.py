# -*- coding:utf-8 -*-
from __future__ import division
import traceback
import datetime as dt
import requests
from struct import unpack
import mysql
import time
import os,glob
import operator as op
from multiprocessing import Process,freeze_support
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from lxml import html

from pyutils import utils
from idlelib import query
###############################################################################
# name      : stock.py
# author    : awen.zhu@hotmail.com
# created   : 2017-10-10
# purpose   : the script extracts tdx.com.cn's data files and then 
#             parse/load it into database
# changelist: 2018/2/25 python2.7 to python3.6
# copyright : copyright (c) zhuyunsheng awen.zhu@hotmail.com all rights received  
# chromedrive download address : http://chromedriver.storage.googleapis.com/index.html
################################################################################

class istock(object):
    def __init__(self,):
        self.urlbase="http://hq.sinajs.cn/list=%s"
        self.watchlist=['sh600050','sz300494','sh600875','sz000598','sh600458','sz002433']
        self.multi=4
        self.curraccount={"avaliablebalance":100000,"currdate":dt.datetime.strptime('2017-09-12','%Y-%m-%d'),'sh600050':{'totalamt':0,"totalprice":0,"availableamt":0,"currops":[]}}
        self.sktcode=[os.path.basename(f).split('.')[0] for f in glob.glob(r'C:\zd_ztzq\vipdoc\sz\lday\*.day')]
        self.urlmap = { 'urlbase':'http://hq.sinajs.cn/list=%s',
                        'cs':'http://f10.eastmoney.com/f10_v2/CompanySurvey.aspx?code=%s',
                        'sh':'http://f10.eastmoney.com/ShareholderResearch/Index?type=web&code=%s',
                        'fa':'http://f10.eastmoney.com/NewFinanceAnalysis/Index?type=web&code=%s',
                        'cm':'http://f10.eastmoney.com/CompanyManagement/Index?type=web&code=%s',
                        'ex':'http://data.eastmoney.com/executive/%s.html',
                        'regrptsse':'http://www.sse.com.cn/disclosure/listedinfo/regular/',
                        'regrptszse':'http://www.szse.cn/disclosure/listed/fixed/index.html'}
        self.pyutils = utils()
    def _getStockInfo(self):
        data = requests.get(self.urlmap['urlbase']%','.join(self.watchlist))
        for l in data.readlines():
            print ( l.decode('gb18030').strip() )
            #for e in l.split(','):print e.decode('gb18030')
    def getQuaterByDelta(self,begindate=None,enddate=None):
        rs = []
        begindate = dt.datetime.now() if begindate is None else dt.datetime.strptime(begindate,'%Y-%m-%d')
        enddate = begindate+dt.timedelta(days=-540)
        while begindate > enddate:
            month = (begindate.month - 1) - (begindate.month - 1) % 3 + 1
            if month == 10:
                newdate = dt.datetime(begindate.year + 1, 1, 1) + dt.timedelta(days=-1)
            else:
                newdate = dt.datetime(begindate.year, month + 3, 1) + dt.timedelta(days=-1)
            nd = dt.datetime.strftime(newdate,'%Y-%m-%d')
            if newdate not in rs:
                rs.append(newdate)
            begindate = begindate+dt.timedelta(days=-30)
        return (rs)            
    def stock1day(self,md=None):
        print ("start")
        self.dfs=r'C:\zd_ztzq\vipdoc\*\lday\*.day'
        self.alldatafiles = glob.glob(self.dfs)
        print (self.alldatafiles)
        for f in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
            with open(f,'rb') as fh:
                print ( "processing with data file : %s"%f )
                scode = os.path.basename(f).split('.')[0]
                with mysql.mysql() as db:
                    fc = fh.read()
                    d=[]
                    db._cursor.execute("""delete from tb_stk_1day where scode = '{}'""".format(scode))
                    db._conn.commit()
                    firstrow=0
                    lastema12,lasteam26,lastdea=0,0,0
                    while fc:
                        rawdata = unpack('IIIIIfII',fc[:32])
                        sdate = dt.datetime.strptime(str(rawdata[0]),'%Y%m%d')
                        sopen = float(rawdata[1]/100)
                        shigh = float(rawdata[2]/100)
                        slow = float(rawdata[3]/100)
                        sclose = float(rawdata[4]/100)
                        samt  = int(rawdata[5])
                        svol = int(rawdata[6])
                        if firstrow == 0:
                            ema12,ema26,dif,dea = sclose,sclose,0,0
                        else:
                            ema12 = (2*sclose+(12-1)*lastema12)/(12+1)
                            ema26 = (2*sclose+(26-1)*lasteam26)/(26+1)
                            dif =  ema12 - ema26
                            dea = (2*dif + (9-1)*lastdea)/(9+1)
                        macd = 2*(dif - dea)
                        lastema12 = ema12
                        lasteam26 = ema26
                        lastdea = dea
                        firstrow += 1
                        d.append((scode,sdate,sopen,shigh,slow,sclose,samt,svol,round(ema12,2),round(ema26,2),round(dif,2),round(dea,2),round(macd,2)))
                        fc = fc[32:]
                    if d:
                        db._cursor.executemany("insert into tb_stk_1day values(?,?,?,?,?,?,?,?,?,?,?,?,?)",d)
                        db._conn.commit()
        print ("well done!")

    def f10_CompanyProfile(self,scode=None,browser=None):
        wait = WebDriverWait(browser, 10)
        browser.get(self.urlmap['cs']%scode)
        wait.until(lambda x:x.find_elements_by_xpath(r"//table[@id='Table0']"))
        pagesource = browser.page_source
        with mysql.mysql() as db:
            ds=[]
            isexist = db._cursor.execute("select count(*) from tb_stk_companyprofile where scode = '%s'"%scode).fetchone()[0]
            if isexist: return
            ds.append(scode)                
            tree = html.fromstring(pagesource)
            th = tree.xpath(r"//table[@id='Table0']/tbody/tr/th")
            td = tree.xpath(r"//table[@id='Table0']/tbody/tr/td")
            if len(th) > 0:
                for i in range(len(th)):
                    ds.append(td[i].text.strip())
                    #print ("%s=%s"%(th[i].text.strip(),td[i].text.strip()))
                db._cursor.execute("delete from tb_stk_companyprofile where scode = '%s'"%scode)
                db._cursor.execute("""insert into tb_stk_companyprofile(scode,comp_name_cn,comp_name_en,former_name,
                                    A_code,A_short_name,B_code,B_short_name,H_code,H_short_name,Invest_category,
                                    Buss_category_em,IPO_Exchange,Buss_category_csrc,GM,legal_representative,
                                    secretary,chairman,invest_buss_agent,Independent_directors,contact_tel,
                                    contact_email,contact_fax,company_website,buss_addr,registry_addr,
                                    region,contact_postcode,registered_capital,IC_Reg_num,emp_num,manager_num,
                                    law_firm,accounting_firm,About_us,buss_scope) values(?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?,?,?,?,?,
                                    ?,?,?,?,?,?)""",ds)
                db._conn.commit()
                print ("loaded company profile data for stock code %s"%scode)
    def f10_ShareHolder(self,scode=None,browser=None):
        """ get data from eastmoney, looks like the data refreshed a little bit delay.
        we need parsing newest data from http://www.szse.cn and shse.cn  """
        try:
            wait = WebDriverWait(browser, 10)
            browser.get(self.urlmap['sh']%scode)
            if browser.title == '无F10资料':
                print ("No data found.")
                return False
            wait.until(lambda x:x.find_elements_by_xpath(r"//div[@id='templateDiv']"))
            pagesource = browser.page_source
            #print (pagesource)
            tree = html.fromstring(pagesource)
            for tag in ['TTCS_Table_Div','TTS_Table_Div']:
                tbd = tree.xpath(r"//div[@id='%s']/table"%tag)
                #quaters = [i.text for i in tree.xpath(r"//div/div/div[@class='tab']/ul//span")]    
                tabvalues=[]
                for i,tb in enumerate(tbd):     
                    if tag == 'TTCS_Table_Div':
                        quaters = [i.text for i in tree.xpath(r"//div[@id='sdltgd']/parent::div/div[@class='content']//ul//span")]
                        #quaters = [i.text for i in tree.xpath(r"//div[@id='sdltgd']/./..//div[@class='tab']/ul//span")]                        
                        trs = tb.xpath(r"./tbody/tr[position() > 2 and position() < 13]") 
                        acctyp = '十大流通股东'
                    else:
                        quaters = [i.text for i in tree.xpath(r"//div[@id='sdgd']/parent::div/div[@class='content']//ul//span")] 
                        #quaters = [i.text for i in tree.xpath(r"//div[@id='sdgd']/./..//div[@class='tab']/ul//span")]
                        trs = tb.xpath(r"./tbody/tr[position() > 1 and position() < 12]") 
                        acctyp = '十大股东'
                    #print ("tag=%s,quaters=%s"%(tag,quaters))
                    for tr in trs:
                        if tag == 'TTS_Table_Div':
                            vs = tr.xpath(r"./th|td")
                        else:
                            vs = tr.xpath(r"./td|th/em")
                        r = []
                        r.append(scode)
                        r.append(quaters[i])
                        r.append(acctyp)
                        for j,v in enumerate(vs):
                            if tag == 'TTS_Table_Div' and j==2:
                                r.append('')
                            tx = v.text.strip() if v.text is not None else v.text
                            r.append(tx)
                        if len(r) == 11 and '合计' not in r:
                            tabvalues.append(r)
                #print ("tabvalues=%s"%tabvalues)
                if len(tabvalues)>0:
                    with mysql.mysql() as db:
                        sql = """select count(*) 
                                   from tb_stk_shareholder_top10 
                                  where scode = '%s'
                                    and top10_acct_typ = '%s'
                                    and report_date in (%s)
                              """%(scode,acctyp,','.join( "'{}'".format(x) for x in quaters))
                        #print ("sql=%s"%sql)
                        isexists = db._cursor.execute(sql).fetchone()[0]
                        print ("isexists=%s,tabvalues=%s"%(isexists,len(tabvalues)))
                        if isexists < len(tabvalues):
                            db._cursor.execute(""" delete from tb_stk_shareholder_top10 
                                  where scode = '%s'
                                    and top10_acct_typ = '%s'
                                    and report_date in (%s)
                              """%(scode,acctyp,','.join( "'{}'".format(x) for x in quaters)))
                            db._conn.commit()
                            db._cursor.executemany("""insert into tb_stk_shareholder_top10(scode,report_date,top10_acct_typ,order_no,acct_name_cn,
                                                                                       acct_typ,stk_typ,stk_cnt,stk_cnt_rate,isincrease,chg_rate) 
                                                                                       values(?,?,?,?,?,?,?,?,?,?,?)""",tabvalues)
                        print ("loaded share holder top10 data for stock code %s"%scode)
                else:
                    print ("can not fetch the data from the website.")
        except Exception as e:
            print ("tag=%s,quaters=%s,r=%s"%(tag,quaters,r))
            print ("sql=%s"%sql)
            print ("values=%s"%tabvalues)
            raise traceback.format_exc(e)
    def f10_Execs(self,scode=None,browser=None):
        try:
            wait = WebDriverWait(browser, 10)
            browser.get(self.urlmap['cm']%scode)
            if browser.title == '无F10资料':
                print ("No data found.")
                return False
            wait.until(lambda x:x.find_elements_by_xpath(r"//div[@id='templateDiv']"))
            pagesource = browser.page_source
            tree = html.fromstring(pagesource)
            execs = tree.xpath('//div[@id="gglb"]/parent::div/div/table/tbody/tr[position()>1]')
            tabvalues = []
            for e in execs:
                vs = e.xpath('./td')        
                r = [ v.text for v in vs]        
                jobdate = e.xpath("//div[@id='glcjj']/parent::div/div/table[%s]/tbody/tr[last()]/td/child::text()"%vs[0].text)[-1]
                cv = e.xpath("//div[@id='glcjj']/parent::div/div/table[%s]/tbody/tr[2]/td[3]/p"%vs[0].text)[0]
                r.append(scode)
                r.append(jobdate.strip() if jobdate is not None else jobdate)
                r.append(cv.text)
                tabvalues.append(r)
            if len(tabvalues)>0:
                with mysql.mysql() as db:
                    sql = "select count(*) from tb_stk_execs where scode = '%s'"%scode
                    isexists = db._cursor.execute(sql).fetchone()[0]
                    if isexists != len(tabvalues) :
                        db._cursor.execute("delete from tb_stk_execs where scode = '%s'")
                        db._conn.commit()
                    db._cursor.executemany("insert into tb_stk_execs(seq,ename,gender,age,edu,job_title,scode,job_date,cv) values(?,?,?,?,?,?,?,?,?)",tabvalues)
                    print ("loaded execs data for stock code %s"%scode)
        except Exception as e:
            print ("r=%s"%r)
            print ("sql=%s"%sql)
            print ("values=%s"%tabvalues)
            raise traceback.format_exc(e)

    def f10_ExecHoldInfo(self,scode=None,browser=None):
        """Extract shareholding of managers from source(web site: eastmoney.com) and then put it into database.
        see the variable urlmap for full url string.
        Parameters:
        -----------
        scode : string
            stock code, like 'sh6000001', 'sz0000001'
        browser : object
            an instance from selenium's web driver.
        Returns:
        --------
        True : if data found and loaded.
        False : if no data found.
        """
        print ("processing with url=%s"%self.urlmap['ex']%scode[2:])
        wait = WebDriverWait(browser, 10)
        browser.get(self.urlmap['ex']%scode[2:])
        if  'undefined' in browser.title:
            print ("No data found.")
            return False
        wait.until(lambda x:x.find_elements_by_xpath(r"//div[@id='bdmx_table_pager']"))
        if browser.find_element_by_xpath('//div[@id="bdmx_table_pager"]').get_attribute('style'):
            totalpages = 1
        else:
            totalpages = browser.find_element_by_xpath('//div[@id="bdmx_table_pager"]/div/a[last()-1]').text
        tree = html.fromstring( browser.page_source )
        if int(totalpages) < 10:
            execs = tree.xpath('//div[@id="bdmx_table"]/table/tbody/tr')
            tabvalues = []
            for e in execs:
                r = []
                r.append(scode)
                for td in e.xpath('./td'):
                    v = td.text.strip() if td.text is not None else ''
                    if len(v)>0:
                        r.append(v)
                    else:
                        v = td.xpath('./a|span')
                        r.append(v[0].text if len(v)>0 else '')
                tabvalues.append(r)
            #print ("processing with current page %s"%browser.find_element_by_id('bdmx_table').text[0:30])
            if int(totalpages) > 1:
                while 1:
                    time.sleep(2)
                    nextpage = browser.find_element_by_xpath('//div[@id="bdmx_table_pager"]/div/a[last()]').text
                    if nextpage == '下一页':
                        browser.find_element_by_xpath('//div[@id="bdmx_table_pager"]/div/a[last()]').click()
                        wait.until(lambda x:x.find_elements_by_xpath(r"//div[@id='bdmx_table']"))
                        tree = html.fromstring( browser.page_source )
                        execs = tree.xpath('//div[@id="bdmx_table"]/table/tbody/tr')
                        for e in execs:
                            r = []
                            r.append(scode)
                            for td in e.xpath('./td'):
                                v = td.text.strip() if td.text is not None else ''
                                if len(v)>0:
                                    r.append(v)
                                else:
                                    v = td.xpath('./a|span')
                                    r.append(v[0].text if len(v)>0 else '')
                            tabvalues.append(r)                
                        #print ("processing with next page %s"%browser.find_element_by_id('bdmx_table').text[0:30])
                    else:
                        #print ("we are done")
                        break
            if len(tabvalues[0]) == 15:
                #print (len(tabvalues),tabvalues)
                with mysql.mysql() as db:
                    isexists = db._cursor.execute("select count(scode) from tb_stk_exholderchg where scode = '%s'"%scode).fetchone()[0]
                    if isexists != len(tabvalues):                        
                        db._cursor.execute("delete from tb_stk_exholderchg where scode = '%s'"%scode)
                        db._conn.commit()
                        db._cursor.executemany("""insert into tb_stk_exholderchg(scode,chg_date,chg_scode,chg_sname,chg_person,
                                                chg_cnt,chg_price_avg,chg_amt,chg_reason,chg_rate,
                                                stk_cnt_afterchg,stk_typ,cxo_name,cxo_job_title,relation_chg_cxo)
                                                values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                                                """,tabvalues)
                print ("data loaded successfully.")
        else:
            print("%s probably is a index stock"%scode)
        return True

    def regReportSSE(self,scode='600000'):
        """Download regular report data (pdf file type) from shanghai market for future extraction."""
        try:
            today = dt.datetime.today()
            start_date = dt.datetime.strftime(today-dt.timedelta(days=90),'%Y-%m-%d')
            end_date = dt.datetime.strftime(today,'%Y-%m-%d')
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
            chrome_options.add_argument('--headless')
            #chrome_options.add_argument('--window-size=1920x1080')
            chrome_options.add_argument('--disable-gpu')
            #chrome_options.add_experimental_option("detach", True)
            browser = webdriver.Chrome(options=chrome_options)
            browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {get: () => undefined})""",})
            browser.maximize_window()
            headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'Accept-Encoding': 'gzip, deflate',
               'Connection': 'keep-alive'
               }
            browser.get(self.urlmap['regrptsse'])
            # we need to waiting for page loaded then do the next steps to avoid the click event does not effect anything.
            WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.XPATH,'//*[@id="tabs-658545"]//table/tbody')))
            # send values via javascript directly, note: if the option headless is set up, 'window-size' option should be set up accordingly
            # otherwise it will causing an error "element not interactable"
            for k,v in {'inputCode':scode,'start_date':start_date,'end_date':end_date}.items():
                #js = "document.getElementById('%s').removeAttribute('readonly')"%i
                js = "document.getElementById('%s').value='%s'"%(k,v)
                browser.execute_script(js)
            browser.execute_script("document.getElementById('btnQuery').click()")
            time.sleep(1)
            #WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.XPATH,'//*[@id="tabs-658545"]//table/tbody')))
            outerHTML = browser.execute_script("return document.getElementById('tabs-658545').outerHTML")
            #outerHTML = WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.XPATH,'//*[@id="tabs-658545"]//table/tbody')))
            self.pyutils.writedisk(filename='pagesource.txt', content=outerHTML.encode('utf-8'))
            #root = html.fromstring(outerHTML)
            #browser.find_element_by_xpath('//*[@id="btnQuery"]').click()
            isnextpage = WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.CLASS_NAME,'page-con-table')))            
            self.pyutils.writedisk(filename='pagesource.txt', content=browser.page_source.encode('utf-8'))
            if len(isnextpage.get_attribute('style')) > 0:
                allpages = 1
            else:
                allpages = int(isnextpage.find_element_by_xpath('./nav/ul/li[last()-1]/a').text)
            tds = browser.find_element_by_xpath('//div[@id="tabs-658545"]/div[1]/div/table/tbody/tr/td')
            print("Total page = %s"%allpages)
            for pg in range(1,allpages+1,1):
                print ("processing with page = %s"%pg,'//div[@class="page-con-table"]//li/a[@page="%s"]'%pg)
                if allpages > 1:
                    WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.XPATH,'//div[@class="page-con-table"]//li/a[@page="%s"]'%pg))).click()
                    WebDriverWait(browser, 10,1).until(EC.presence_of_element_located((By.XPATH,'//div[@id="tabs-658545"]')))
                trs = browser.find_elements_by_xpath('//div[@id="tabs-658545"]/div[1]/div/table/tbody/tr[position()>1]')
                for tr in trs:
                    stockcode = tr.find_elements_by_xpath('./td[position()=1]')[0].text
                    if stockcode == '暂无数据':break
                    stockname = tr.find_elements_by_xpath('./td[position()=2]')[0].text
                    rptname   = tr.find_elements_by_xpath('./td[position()=3]/a')[0].text
                    rptfile   = tr.find_elements_by_xpath('./td[position()=3]/a')[0].get_attribute('href')
                    rptdate   = tr.find_elements_by_xpath('./td[position()=3]')[0].get_attribute('data-time')
                    filename = './DA/rpt/sh/%s_%s_%s_%s.pdf'%(stockcode,stockname.replace('*','x'),rptdate.replace(':','-').strip(),rptname)
                    print("filename = %s rptfile=%s"%(filename,rptfile))
                    self.pyutils.downloadinchuck(rptfile, headers, filename)
            print ("all done")
        except:
            raise
        finally:
            #pass
            browser.close()
    def regReportSZSE(self):
        """Download regular report data (pdf file type) from shenzhen market for future extraction."""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            browser = webdriver.Chrome(options=chrome_options)
            browser.maximize_window()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
                       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                       'Connection': 'keep-alive',
                       'Range': 'bytes=0-'
                      }
            wait = WebDriverWait(browser, 30,1)
            browser.get(self.urlmap['regrptszse'])
            allpages = wait.until(EC.presence_of_element_located((By.XPATH,'//div[@id="disclosure-table"]//span[@class="num-all"]')))
            for pg in range(int(allpages.text)):
                print ("starting process with page %s of %s"%(pg,allpages.text))                
                wait.until(EC.presence_of_element_located((By.XPATH,'//ul[@id="paginator"]/li/a[@data-pi="%s"]'%pg))).click()
                rows = wait.until(EC.presence_of_all_elements_located((By.XPATH,'//div[@id="disclosure-table"]//tbody/tr')))
                for r in rows:
                    scode = r.find_element_by_class_name('title-code').text
                    sname = r.find_element_by_class_name('title-name').text
                    rpt = r.find_element_by_class_name('text-title-box')
                    rptname = rpt.find_element_by_xpath('./a/span').text
                    rptfile = 'http://disc.static.szse.cn/download'+rpt.find_element_by_xpath('./a').get_attribute('attachpath')
                    rptdate = r.find_element_by_class_name('text-time').text
                    filename = './DA/rpt/sz/%s_%s_%s_%s.pdf'%(scode,sname.replace('*','x'),rptdate.replace(':','-').strip(),rptname)
                    print ("filename = %s rptfile=%s"%(filename,rptfile))
                    # not sure why but it cannot download files by using multiprocess here. 
                    # if we setup threadcnt>1 it will error out with bad Content-Length
                    self.pyutils.download(rptfile, headers, filename, threadcnt=1)
                break
        except:
            self.pyutils.createfile('./DA/rpt/sz/%s_%s_%s_%s.failed'%(scode,sname.replace('*','x'),rptdate.replace(':','-').strip()))
        finally:
            browser.close()
    def f10(self):
        try:
            scode='sz300142'
            # 添加无头headlesss
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-gpu')
            browser = webdriver.Chrome(options=chrome_options)
            # browser = webdriver.PhantomJS()
            browser.maximize_window()
            #page = browser.find_element_by_id('TTCS_Table_Div')
            #page = browser.find_element_by_xpath(r"//div[@id='TTCS_Table_Div']/table/tbody/tr[position()=3]")
            #print (page.text)
            self.sktcode = ['sz300507']
            for scode in self.sktcode:                
                #self.f10_ExecHoldInfo(scode, browser)
                self.f10_Execs(scode, browser)
                #self.f10_CompanyProfile(scode,pagesource)
                #self.f10_ShareHolder(scode, browser)
                #time.sleep(1)
        except Exception as e:
            raise traceback.format_exc(e)
        finally:
            browser.quit()
    def stock1min(self,md=None):
        self.dfs=r'C:\zd_ztzq\vipdoc\*\minline\*.lc1'
        self.alldatafiles = glob.glob(self.dfs)
        with mysql.mysql() as db:
            for fl in self.alldatafiles[md::(None if self.multi == 1 else self.multi)]:
                scode=os.path.basename(fl).split('.')[0]
                with open(fl,'rb') as f:
                    print ("start process file : %s"%fl)
                    fc = f.read()
                    d=[]
                    sql="""select ifnull(max(sdate),str_to_date('1980-01-01 12:12:12','%%Y-%%m-%%d %%H:%%M:%%S')) from tb_stk_1min where scode = '%s'"""%scode
                    maxdate = db._cursor.execute(sql).fetchone()[0]
                    if maxdate is None: maxdate = dt.datetime.strptime('1980-01-01 10:10:10','%Y-%m-%d %H:%M:%S')
                    if dt.datetime.today() > maxdate:
                        while fc:
                            rawdata = unpack('hhfffffii',fc[:32])
                            sdate = dt.datetime.strptime("%s-%02d-%02d %02d:%02d:%02d"%(int(rawdata[0]/2048)+2004,int(op.mod(rawdata[0],2048)/100),op.mod(op.mod(rawdata[0],2048),100),int(rawdata[1]/60),op.mod(rawdata[1],60),0),'%Y-%m-%d %H:%M:%S')                            
                            ropen,rhigh,rlow,rclose,ramt,rvol = "%.2f"%rawdata[2],"%.2f"%rawdata[3],"%.2f"%rawdata[4],"%.2f"%rawdata[5],"%.2f"%rawdata[6],"%d"%rawdata[7]
                            if sdate > maxdate:
                                d.append((scode,sdate,ropen,rhigh,rlow,rclose,ramt,rvol))
                                #print scode,datetime.datetime.strptime(sdate,'%Y-%m-%d %H:%M:%S'),ropen,rhigh,rlow,rclose,ramt,rvol
                            fc = fc[32:]
                        if d:
                            db._cursor.executemany("insert into tb_stk_1min values(?,?,?,?,?,?,?,?)",d)
                            db._conn.commit()

    def run(self):
        for i in range(self.multi):
            p=Process(target=self.stock1day,args=(i,))
            p.start()
        p.join()

if __name__ == "__main__":
    freeze_support()
    istk = istock()
    #istk._getStockInfo()
    #istk.stock1day(0)
    #istk.f10()
    #istk.run()
    istk.regReportSSE()
    #istk.stock1min()
    #istk.backtrace()
    #istk.buy(scode='sh600050',amt=10000,price=7.11,opdate=datetime.datetime.strptime('2017-09-11','%Y-%m-%d'))
    
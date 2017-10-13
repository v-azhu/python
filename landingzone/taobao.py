# -*- coding: utf-8 -*-
import requests  
import re
import traceback  

"""
json data unpack:
for a in js.items()[1][1]["itemlist"]["data"]["auctions"]:
            for k,v in a.items():
                if v:
                    print k,v
            print "*"*20

output:
category 50050732
raw_title 纽顿果园新鲜水果苹果 正宗烟台栖霞红富士苹果好吃的5斤装1箱装
i2iTags {u'samestyle': {u'url': u''}, u'similar': {u'url': u'/search?type=similar&app=i2i&rec_type=1&uniqpid=&nid=528411306657'}}
user_id 2831531036
title 纽顿果园新鲜水果<span class=H>苹果</span> 正宗烟台栖霞红富士<span class=H>苹果</span>好吃的5斤装1箱装
shopcard {u'encryptedUserId': u'UvCgGvF8GvFNGMgTT', u'service': [476, -1, 121], u'sellerCredit': 13, u'isTmall': False, u'delivery': [471, -1, 188], u'totalRate': 9895, u'levelClasses': [{u'levelClass': u'icon-supple-level-guan'}, {u'levelClass': u'icon-supple-level-guan'}, {u'levelClass': u'icon-supple-level-guan'}], u'description': [470, -1, 165]}
item_loc 山东 烟台
nid 528411306657
nick niudunguoyuan
comment_count 43923
view_price 28.90
view_fee 0.00
view_sales 6190人付款
detail_url //item.taobao.com/item.htm?id=528411306657&ns=1&abbucket=16#detail
shopLink //store.taobao.com/shop/view_shop.htm?user_number_id=2831531036
pic_url //g-search2.alicdn.com/img/bao/uploaded/i4/i1/2831531036/TB2zklSyHBmpuFjSZFuXXaG_XXa_!!2831531036.jpg
comment_url //item.taobao.com/item.htm?id=528411306657&ns=1&abbucket=16&on_comment=1
icon [{u'outer_text': u'0', u'trace': u'srpservice', u'title': u'\u5ea6\u91cf\u5355\u4f4d', u'dom_class': u'icon-service-duliangheng', u'show_type': u'0', u'html': u'<span class="icon-pit icon-service-duliang"><b>5.78</b>\u5143/\u65a4</span>', u'innerText': u'\u5ea6\u91cf\u5355\u4f4d', u'position': u'1', u'icon_key': u'icon-service-duliangheng', u'icon_category': u'cat_special', u'traceIdx': 61}]
"""

def getHTMLText(url):  
    try:  
        r = requests.get(url, timeout = 30)  
        r.raise_for_status()  
        r.encoding= r.apparent_encoding  
        return r.text  
    except:  
        return ""  
  
  
def paserPage(list,html):  
    try:  
        plt = re.findall(r'\"view_price\"\:\"[\d.]*\"',html)  
        tlt = re.findall(r'\"raw_title\"\:\".*?\"',html)  
        sls = re.findall(r'\"view_sales\"\:\".*?\"',html)  
        for i in range(len(plt)):  
            price = eval(plt[i].split(':')[1])  
            title = eval(tlt[i].split(':')[1])  
            sales = eval(sls[i].split(':')[1])  
            list.append([price,title,sales])  
    except Exception as e:  
        print(traceback.format_exc(e))   
  
  
def printGoodsList(list):  
    tplt ="{:4}\t{:8}\t{:4}\t{:16}"  
    print(tplt.format("seq", "price",  "sales", "good"))  
    count = 0  
    for g in list:  
        count=count+1  
        print(tplt.format(count,g[0],g[2],g[1]))  
        
  
def main():  
    goods = 'ƻ��'  
    depth = 3
    start_url = 'https://s.taobao.com/search?q=' + goods  
    infoList = []  
    for i in range(depth):  
        try:  
            url = start_url + '&s=' + str(44*i)  
            html = getHTMLText(url)  
            shtml=html
            #print type(shtml)
            #with open('e:/goods_{}.txt'.format(str(i)),'w') as f:f.write(shtml) 
            paserPage(infoList,html)             
        except:  
            continue  
    #print(infoList)  
    printGoodsList(infoList)  

if __name__ == "__main__":
    main()
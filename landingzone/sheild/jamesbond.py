
#jamesbond.py
# -*- coding: utf-8 -*-
import traceback
from lxml import etree as et
import xlwt
import pyutils
import base64

def doParse(xml,sheetHandler,sheetName,fields):
    u = pyutils.utils()
    counter = u.counter(1,1,65527)
    sheetHandler.write(0,1,'KEY')
    sheetHandler.write(0,2,'ENTNAME')
    sheetHandler.write(0,3,'REGNO')
    sheetHandler.write(0,4,'CREDITCODE')
    sheetHandler.write(0,5,'ANCHEYEAR')
    for i,k in enumerate(fields,start=1): sheetHandler.write(0,5+i,k)
    for child in xml.getchildren():         
        if child.xpath('./YEARREPORT/ITEM'):            
            for yrb in child.xpath('./YEARREPORT/ITEM'):
                for items in yrb.xpath('./'+sheetName):
                    for item in items:
                        row=counter.next()
                        sheetHandler.write(row,1,child.xpath('./ORDERLIST/ITEM[1]/KEY')[0].text)
                        sheetHandler.write(row,2,child.xpath('./BASIC/ITEM[1]/ENTNAME')[0].text)
                        sheetHandler.write(row,3,child.xpath('./BASIC/ITEM[1]/REGNO')[0].text)
                        sheetHandler.write(row,4,child.xpath('./BASIC/ITEM[1]/CREDITCODE')[0].text)
                        sheetHandler.write(row,5,yrb.xpath('./YEARREPORTBASIC/ITEM[1]/ANCHEYEAR')[0].text)                     
                        for idx,field in enumerate(fields,start=1): sheetHandler.write(row,5+idx,item.xpath('./'+field)[0].text)
        if sheetName=='EXCEPTIONLIST' and child.xpath('./EXCEPTIONLIST/ITEM'):
            for items in child.xpath('./EXCEPTIONLIST/ITEM'):
                row=counter.next()
                sheetHandler.write(row,1,child.xpath('./ORDERLIST/ITEM[1]/KEY')[0].text)
                sheetHandler.write(row,2,child.xpath('./BASIC/ITEM[1]/ENTNAME')[0].text)
                sheetHandler.write(row,3,child.xpath('./BASIC/ITEM[1]/REGNO')[0].text)
                sheetHandler.write(row,4,child.xpath('./BASIC/ITEM[1]/CREDITCODE')[0].text) 
                if child.xpath('./YEARREPORTBASIC/ITEM[1]/ANCHEYEAR'):
                    sheetHandler.write(row,5,child.xpath('./YEARREPORTBASIC/ITEM[1]/ANCHEYEAR')[0].text)
                else:
                    sheetHandler.write(row,5,'')                   
                for item in items:
                    for idx,c in enumerate(fields,start=1):
                        if item.text and c == item.tag:
                            if c=='DETAILSTEXT' and item.text is not None:
                                sheetHandler.write(row,5+idx,base64.b64decode(item.text).decode('UTF8'))
                            else:
                                sheetHandler.write(row,5+idx,item.text)
        #if row>10:break
def corpNameSocialNo(wb):
    try:             
        tree=et.parse('e:/py2.xml')
        root = tree.getroot()
        
        YEARREPORTBASIC=['ENTNAME','REGNO','CREDITNO','ANCHEYEAR','ANCHEDATE','TEL','ADDR','POSTALCODE','EMAIL','BUSST','ENTTYPE']
        sheetHandler = wb.add_sheet(u'YEARREPORTBASIC', cell_overwrite_ok=True)   
        doParse(root,sheetHandler,'YEARREPORTBASIC',YEARREPORTBASIC)
           
        ############
        YEARREPORTSUBCAPITAL=['INV','LISUBCONAM','CONDATE','CONFORM','CURRENCY']
        sheetHandler = wb.add_sheet(u'YEARREPORTSUBCAPITAL', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'YEARREPORTSUBCAPITAL',YEARREPORTSUBCAPITAL)
      
        ############
        YEARREPORTALTERSTOCKINFO=['INV','TRANSAMPR','TRANSAMAFT','ALTDATE']
        sheetHandler = wb.add_sheet(u'YEARREPORTALTERSTOCKINFO', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'YEARREPORTALTERSTOCKINFO',YEARREPORTALTERSTOCKINFO)
       
       
        ############
        YEARREPORTWEBSITEINFO=['WEBTYPE','WEBSITNAME','DOMAIN']
        sheetHandler = wb.add_sheet(u'YEARREPORTWEBSITEINFO', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'YEARREPORTWEBSITEINFO',YEARREPORTWEBSITEINFO)
                               
        ############
        YEARREPORTPAIDUPCAPITAL=['INV','LIACCONAM','CONDATE','CONFORM','CURRENCY']
        sheetHandler = wb.add_sheet(u'YEARREPORTPAIDUPCAPITAL', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'YEARREPORTPAIDUPCAPITAL',YEARREPORTPAIDUPCAPITAL)
       
                               
        ############
        YEARREPORTFORINVESTMENT=['ENTNAME','REGNO','CREDITNO']
        sheetHandler = wb.add_sheet(u'YEARREPORTFORINVESTMENT', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'YEARREPORTFORINVESTMENT',YEARREPORTFORINVESTMENT)
                             
               
        ############
        YEARREPORTFORGUARANTEEINFO=['MORE','MORTGAGOR','PRICLASECKIND','PRICLASECAM','PEFPERFORM','PEFPERTO','GUARANPERIOD','GATYPE']
        sheetHandler = wb.add_sheet(u'YEARREPORTFORGUARANTEEINFO', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'YEARREPORTFORGUARANTEEINFO',YEARREPORTFORGUARANTEEINFO)
                        
        ############
        EXCEPTIONLIST=['REGNO','ENTNAME','STATE','SHXYDM','DETAILSTEXT','INDATE','OUTDATE']
        sheetHandler = wb.add_sheet(u'EXCEPTIONLIST', cell_overwrite_ok=True)
        doParse(root,sheetHandler,'EXCEPTIONLIST',EXCEPTIONLIST)

    except Exception as e:
        print traceback.format_exc(e) 
def runner077():
    wb=xlwt.Workbook()
    corpNameSocialNo(wb)
    wb.save('e:/077_2.xls') 
        
if __name__ == "__main__":
    runner077()
    
# -*- coding:utf-8 -*-
import pyodbc
###############################################################################
# name      : mysql.py
# author    : carl_zys@163.com
# created   : 2017-10-10
# purpose   : mysql database operation object.
# copyright : copyright (c) zhuyunsheng carl_zys@163.com all rights received  
################################################################################
class mysql(object):
    def __init__(self):
        self._dsn='stdb'
    def __enter__(self):
        self._conn=pyodbc.connect("DSN=%s"%self._dsn)
        self._cursor=self._conn.cursor()
        return self
    def __exit__(self,type,value,traceback):
        if hasattr(self,'_cursor'):
            self._cursor.close()
        if hasattr(self,'_conn'):
            self._conn.commit()
            self._conn.close()
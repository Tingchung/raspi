# -*- coding: utf-8 -*-

# Module : database.Sqlite_access
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.0
# Last Revise : 2021/1/16


import os
import sys
import json
import sqlite3


# Func : execute
# Desc : 執行 SQL 指令
def execute(thisDbPath:str, thisSqlCommand:str):
    # 寫入到資料庫
    _sqlstring = thisSqlCommand
    objCon = sqlite3.connect(thisDbPath)
    objCursor = objCon.cursor()
    objCursor.execute(_sqlstring)
    
    objCon.commit()
    objCon.close()

    return 


# Func : query
# Desc : 查詢資料
def query(thisDbPath:str, thisSqlCommand):
    _sqlstring = thisSqlCommand
    objCon = sqlite3.connect(thisDbPath)
    objCursor = objCon.cursor()
    _Result = objCursor.execute(_sqlstring).fetchall()

    objCon.close()

    return _Result
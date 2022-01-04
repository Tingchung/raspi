# -*- coding: utf-8 -*-

# Module : command
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.3.14
# Last Revise : 2022/1/4


import sys
import os
import socket
import json
from datetime import datetime
from datetime import timedelta
import time
import sqlite3

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "./../../../lib/Cuki.Lib"))

import config
import process_system as processSystem
import process_nccc as nccc
import process_q80 as q80
import process_godex as godex
import process_hprt as hprt
from database import sqlite_access as sqlaccess
from utility import randomTool 



_filepath_db = config.path("~/app_data/file_db/common/db_sys.sqlite")



#==============================================================
#-----[ command access ]--------------------------------------
# 這一節主要是關於命令資料和狀態的存取

# Func : get_unprocess_commandlist 
# Desc : 取得尚未到期且未執行的命令
def get_unprocess_commandList(thisClientId):
    _now = datetime.now()
    _clientId = thisClientId
    _sqlcommand = f"select * from ec_command where executeStatus = 0 and clientid = '{_clientId}' and expiredate >= '{_now}' order by createdate desc"
    db_commandlist = sqlaccess.query(_filepath_db, _sqlcommand)
    
    return db_commandlist


# Func : get_command_by_commandId 
# Desc : 取得指令的命令
def get_command_by_commandId(thisCommandId):
    _commandId = thisCommandId
    _sqlcommand = f"select * from ec_command where commandid = '{_commandId}'"
    db_commandList = sqlaccess.query(_filepath_db, _sqlcommand)

    _result = {}
    if len(db_commandList) > 0:
        _result = db_commandList[0]

    return _result


# Func : add_command
# Desc : 新增命令
def add_command(thisCommand):
    # 整理資料
    _now = datetime.now()
    _string_now = _now.strftime("%Y%m%d")
    _randomString = randomTool.get_randomstring(15)
    _commandId = f"{_string_now}-{_randomString}"
    _clientId = thisCommand["clientId"]
    _commandType = thisCommand["commandType"]
    _method = thisCommand["method"].lower()
    _detail = json.dumps(thisCommand)
    _executeResult = ""
    _isExecuted = 0
    _executeDate = ""
    _expireTimeSpan  = thisCommand["expireTimeSpan"]
    _expireDate = _now + timedelta(seconds=thisCommand["expireTimeSpan"])
    _createdate = _now


    # 寫入到資料庫
    _sqlcommand = f"insert into ec_command values('{_commandId}', '{_clientId}', '{_commandType}', '{_method}', '{_detail}', '{_executeResult}', {_isExecuted}, '{_executeDate}', '{_expireDate}', '{_createdate}')"
    sqlaccess.execute(_filepath_db, _sqlcommand)    
    

    return {
        "isSuccess": True, 
        "message": "", 
        "data": {
            "commandId": _commandId
        }
    }


# Func : set_isProcessing
# Desc : 將命令標記為處理中
def set_isProcessing(thisCommandId:str):
    _sqlCommand = f"update ec_command set executeStatus = 2 where commandId = '{thisCommandId}'"
    sqlaccess.execute(_filepath_db, _sqlCommand)

    return 


# Func : update_executeResult
# Desc : 更新命令的執行結果, 這個函式會將該命令標記為'已執行'
def set_isCompleted(thisCommandId, thisResultJSON):
    _now = datetime.now()
    _string_Result = json.dumps(thisResultJSON)
    _sqlcommand = f"update ec_command set executeResult = '{_string_Result}', executeStatus = 1, executedate = '{_now}' where commandid = '{thisCommandId}'"
    print("===============================")
    print(_sqlcommand)
    print("===============================")
    sqlaccess.execute(_filepath_db, _sqlcommand)

    return



#==============================================================
#-----[ command process ]--------------------------------------
# 這一節主要是關於命令的實際執行

# Func : execute
# Desc : 執行命令
def execute(thisDbCommand):
    _commandId = thisDbCommand[0]
    _commandType = thisDbCommand[2]
    _method = thisDbCommand[3]
    _commandDetail = json.loads(thisDbCommand[4])

    # 將命令標記為處理中
    set_isProcessing(_commandId)
    print("execute commandid : " + _commandId)
    

    # 依照命令的種類呼叫個別函式處理    
    _result_execute = {}
    _isDevMode = False
    print("devMode in commandDetail : " + str("devMode" in _commandDetail))
    if "devMode" in _commandDetail and _commandDetail["devMode"]:
        _isDevMode = True
        _result_execute = process_devTest(_commandId, _commandDetail)
    else:
        try:
            _result_execute = execute_case(_commandId, _commandType, _method, _commandDetail)  
        except:
            _result_execute = {
                "isSuccess": False, 
                "message": "unknow error !!"
            }


    # 將命令標記為已完成
    set_isCompleted(thisDbCommand[0], _result_execute)


    # 整理回傳結果
    _result = {
        "statusType": "Command", 
        "statusCode": "CMD-ERR-000", 
        "commandId": _commandId
    }
    if "data" in _result_execute:
        _result  = _result_execute["data"]


    return _result


# Func : execute_case
# Desc : 依命令種類分類進行執行
def execute_case(thisCommandId, thisCommandType, thisMethod, thisCommandDetail):
    # 整理參數
    _commandId = thisCommandId
    _commandType = thisCommandType
    _method = thisMethod
    _commandDetail = thisCommandDetail


    # ===== 依據 command type 進行 ##前置處理## ================================
    #       處理支付相關作業
    if _commandType == "payment":
        # 取得指定的設備資訊
        _deviceId = _commandDetail["deviceId"]
        _deviceInfo = config.get_deviceInfo("payment", _deviceId)

        # 如果無法從設定檔取得設備資訊
        if _deviceInfo == None:
            _result_execute = {
                "isSuccess": False, 
                "message": "", 
                "data": {
                    "statusCode": "deviceSetting-ERR-001"
                }
            }
            return _result_execute

    #       處理列印相關作業
    if _commandType == "print":
        # 取得指定的設備資訊
        _deviceId = _commandDetail["deviceId"]
        _deviceInfo = config.get_deviceInfo("printer", _deviceId)
        
        # 如果無法從設定檔取得設備資訊
        if _deviceInfo == None:
            _result_execute = {
                "isSuccess": False, 
                "message": "", 
                "data": {
                    "statusCode": "deviceSetting-ERR-002"
                }
            }
            return _result_execute


    # ===== 依 method 選擇執行的函數 ==========================================
    #       處理 "刷卡機" 相關命令
    if _commandType == "payment":
        #       [ NCCC 刷卡機 ]
        if _deviceInfo["type"] == "nccc":
            if _method == "start_payment":
                _result_execute = nccc.start_payment(_commandId, _commandDetail, _deviceInfo)
            if _method == "send_message":
                _result_execute = nccc.send_message(_commandId, _commandDetail, _deviceInfo)
        #       [ Q80 刷卡機 ]
        if _deviceInfo["type"] == "q80":
            if _method == "start_payment":
                _result_execute = q80.start_payment(_commandId, _commandDetail, _deviceInfo)
            if _method == "send_message":
                _result_execute = q80.send_message(_commandId, _commandDetail, _deviceInfo)

    #       處理 "印表" 相關命令
    if _commandType == "print":
        #       [ Godex dt2x ]
        if _deviceInfo["type"] == "godex dt2x":
            _result_execute = godex.dt2x_print(_commandDetail["content"], _deviceInfo["ip"])
        #       [ HPRT tp808 ]
        if _deviceInfo["type"] == "hprt tp808":
            _result_execute = hprt.tp808_print(_commandDetail["content"], _deviceInfo["ip"])

    #       處理 "命令資料" 的操作
    if _commandType == "command":
        if _method == "get_commandlog":
            _result_execute = process_command_getCommandLog(_commandId, _commandDetail)
        elif _method == "get_setting":
            _result_execute = processSystem.setting_get_setting()
        elif _method == "update_setting":
            _result_execute = processSystem.setting_update_setting(_commandDetail["settingString"])


    # 回傳結果
    return _result_execute


# Func : process_command_getCommandLog
# Desc : 取得指定的命令資料
def process_command_getCommandLog(thisCommandId, thisCommandDetail):
    # 取得命令內容
    _targetCommandId = thisCommandDetail["commandId"]
    dbCommand = get_command_by_commandId(_targetCommandId)
    if dbCommand == {}:
        return {
            "isSuccess": False, 
            "statusCode": "CMD-ERR-100"
        }

    # 整理回傳資料
    _commandLog = {
        "commandId": dbCommand[0], 
        "commandType": dbCommand[2],
        "method": dbCommand[3],
        "sourceCommand": dbCommand[4], 
        "executeResult": dbCommand[5], 
        "commandStatus": dbCommand[6], 
        "executeDate": dbCommand[7], 
        "createDate": dbCommand[9]
    }
    _data = {
        "commandId": thisCommandId,
        "statusCode": "CMD-OK-100", 
        "commandLog": _commandLog
    }
    _result = {
        "isSuccess": True, 
        "data": _data
    }

    return _result


# Func : process_test
# Desc : 處理刷卡機交易 (測試用)
def process_devTest(thisCommandId, thisCommandDetail):
    if "devReturn" in thisCommandDetail:
        _result = thisCommandDetail["devReturn"]
    else:
        _result = {
            "isSuccess": True, 
            "data": {
                "statusType": "paymentStatus",
                "statusCode": "P-OK-001"
            }
        }

    time.sleep(1.5)

    return _result






if __name__ == '__main__':
    print(get_command_by_commandId("20210801-tho7TC34Cjy5GzC"))

    
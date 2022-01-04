# -*- coding: utf-8 -*-

# Module : config
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.2
# Last Revise : 2021/8/17


import sys
import os
import socket
import json

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


# Func : Path_Root 
# Desc : 
def path_root():
    _FolderPath_Root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../')
    return _FolderPath_Root


# Func : Path 
# Desc : 
def path(thisPath:str):
    _Path = thisPath.replace('~/', path_root() + '/')
    return _Path


# Func : Get_IP
# Desc :
def get_ip():
    objSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        objSocket.connect(('10.255.255.255', 1))
        _ip = objSocket.getsockname()[0]
    except Exception:
        _ip = '127.0.0.1'
    finally:
        objSocket.close()
    return _ip


#================================================
#-----[ setting.json ]--------------------------------

# Func : setting 
# Desc : 傳回設定檔的內容
def setting():
    _filepath = path("~/app_data/system/setting.json")
    with open(_filepath, "r") as objFile:
        _filecontent = objFile.read()
    _setting = json.loads(_filecontent)

    return _setting


# Func : update_setting 
# Desc : 更新設定檔的內容
def update_setting(thisSetting):
    _filepath = path("~/app_data/system/setting.json")
    _string_setting = json.dumps(thisSetting)

    with open(_filepath, "w", encoding="UTF-8") as objFile:
        _filecontent = objFile.write(_string_setting)
     
    return True


# Func : get_paymentDeviceInfo 
# Desc : 取得指定的設備資訊
def get_deviceInfo(thisDeviceType, thisPaymentDeviceId):
    _setting = setting()
    if thisDeviceType in _setting == False:
        return None

    # 巡覽清單
    _result = None
    for i in range(0, len(_setting[thisDeviceType]), 1):
        if _setting[thisDeviceType][i]["deviceId"] == thisPaymentDeviceId:
            _result = _setting[thisDeviceType][i]
            break


    #回傳結果
    return _result


#======================================================
#-----[ security.json ]--------------------------------

# Func : get_securitySetting 
# Desc : 傳回系統安全設定檔的內容
def get_securitySetting():
    _filepath = path("~/app_data/system/security.json")
    with open(_filepath, "r") as objFile:
        _filecontent = objFile.read()
    _securitySetting = json.loads(_filecontent)

    return _securitySetting


# Func : get_token 
# Desc : 取得系統憑證
def get_token():
    # 取得系統安全設定檔
    _securitySetting = get_securitySetting()

    # 整理回傳資料
    _token = _securitySetting["token"]

    
    return _token
# -*- coding: utf-8 -*-

# Module : Device Web System
# Version : 1.5.25
# Author : Johnny Fang <johnnyfang.tw@gmail.com>


from flask import Flask, request, render_template, send_file
import sys
import os
import json
import random
import importlib
import subprocess
import datetime
import time
import socket

from app_code import config


app = Flask(__name__)


# Page : /js/{jsName}
# Desc : 取得指定的 JS 檔案
@app.route('/<thisType>/<thisJSName>', methods=['GET', 'POST'])
def static_file_load(thisType, thisJSName):
    # 檢查檔案是否存在
    _filepath = config.path(f"~/static/{thisType}/{thisJSName}.{thisType}")
    if os.path.isfile(_filepath) == False:
        return "reject"

    # 載入檔案內容,並改寫 WebSocket Server 的 IP 位置
    with open(_filepath, "r") as objFile:
        _filecontent = objFile.read()

    _hostname = socket.gethostname()
    _ip = socket.gethostbyname(_hostname)
    _ip = config.get_ip()
    _result = _filecontent.replace("127.0.0.1", _ip)

    return _result


# Page : /setup
# Desc : 系統設定頁
@app.route('/setup/<thisSetupToken>', methods=['GET', 'POST'])
def page_setup(thisSetupToken):
    # get security setting 
    _securitySetting = config.get_securitySetting()
    _token = _securitySetting["token"]

    # check the token is match or not
    if thisSetupToken != _token:
        return "token is not match!!"

    # return setup page 
    _file_page = f'setup.html'
    appData = {}

    return render_template(_file_page, appData=appData)


# Page : /devTool
# Desc : 開發者工具頁
@app.route('/devTool', methods=['GET', 'POST'])
def page_devTool():
    _file_page = f'devTool.html'
    _token = config.get_token()

    appData = {
        "token": _token
    }

    return render_template(_file_page, appData=appData)



#===============================================================
#=====[ API ]===================================================


# API : /api/get_setting
# Desc : 取得設定檔內容
@app.route('/api/get_setting', methods=["POST"])
def api_get_setting():
    _param = request.json["Param"]

    # 取得設定檔內容
    _setting = config.setting()

    # 整理回傳資料
    _result = {
        "isSuccess": True,
        "data": {
            "setting": _setting
        }
    }
    _string_result = json.dumps(_result)

    return _string_result


# API : /api/update_setting
# Desc : 更新設定
@app.route('/api/update_setting', methods=['GET', 'POST'])
def api_update_setting():
    _param = request.json["Param"]

    # 取得設定檔內容
    _setting = config.setting()
    _setting["token"] = _param["token"]
    _setting["port_payment"] = _param["port_payment"]

    # 寫回到設定檔
    config.update_setting(_setting)

    return json.dumps({
        "IsSuccess": True,
        "Message": "設定已儲存"
    })


# API : /api/upload_logo
# Desc : upload_logo
@app.route("/api/upload_logo", methods=["POST"])
def API_FileUpload():
    # 整理參數
    objFile = request.files["file"]

    _Result = {
        "IsSuccess": False, 
        "Message": "File can't be null"
    }

    # 檢查檔案是否正確上傳
    if objFile is None:
        return json.dumps(_Result)
    else:
        _FileName = config.path("~/static/img/logo.jpg")
        objFile.save(_FileName)

        # 回傳結果
        _Result = {
            "IsSuccess": True, 
            "Message": ""
        }

        return json.dumps(_Result)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=12000)

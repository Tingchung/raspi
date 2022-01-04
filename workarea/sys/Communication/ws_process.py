#!/usr/bin/env python

# Module        : Command WebSocket Server
# Version	    : 1.5.26
# Last Revise   : 2021/10/14


import os
import sys
import asyncio
from datetime import datetime
from datetime import timedelta
import ssl
import random
import websockets
import json
import pathlib
from app_code import config 
from app_code import command

sys.path.insert(0, config.path('~/../../lib/Cuki.Lib'))
from utility import randomTool 



# Service : handle_process
# Desc : 負責處理命令並回覆處理結果
async def handle_process(websocket, path):
    _clientId = randomTool.get_randomstring(20)
    for i in range(0, 10, 1):
        print(".")
    print(f"client id : {_clientId}")

    # 嘗試先送出一次回應
    try:
        await send_result(websocket, {
            "statusType": "system", 
            "statusCode": "ws-OK-001", 
            "message": "ws_process 連結成功", 
            "data": {
                "dateTime": datetime.now().strftime("%H:%M:%S"),
                "clientId": _clientId
            }
        }, _clientId)
        print("connection success")
    except websockets.exceptions.ConnectionClosed:
        print("connetion fail")
        return


    # 反覆檢查是否有待執行的命令
    _counter_check_connection = 0
    while True:
        # 從資料庫中取得待執行的命令清單
        dbCommandList = command.get_unprocess_commandList(_clientId)
        if len(dbCommandList) > 0:
            _result_send = await send_result(websocket, {
                "statusType": "system", 
                "statusCode": "ws-OK-300", 
                "message": "發現待執行的指令",
                "data": {
                    "dateTime": datetime.now().strftime("%H:%M:%S")
                }
            }, _clientId)
            if _result_send == False:
                print("connection break!")
                break

            # 處理並執行第 1 個命令並回傳執行結果到前端            
            dbCommand = dbCommandList[0]
            _result = command.execute(dbCommand)            

            # 將結果傳回前端
            _result_send = await send_result(websocket, _result, _clientId)
            # print(_result_send)
            if _result_send == False:
                break
        
        await asyncio.sleep(0.5)
        _counter_check_connection += 1


# Func : send_result
# Desc : 將資料傳送給前端
async def send_result(websocket, thisResult, thisProcessId):
    _string_result = json.dumps(thisResult)
    try:
        await websocket.send(_string_result)
    except websockets.exceptions.ConnectionClosed:
        print("send fail")
        return False

    if thisResult == "ack":
        return True

    print("send success")
    print("====================")
    print(thisResult )
    print(f"process id : {thisProcessId}")
    print("====================")

    return True



# Func : devMode_Tool
# Desc : 開發模式工具
async def devMode_Tool(websocket, path):
    _filePath = config.path("~/app_data/file_db/common/statusCode.txt")
    with open(_filePath, "r") as objFile:
        _fileContent = objFile.read()

    if _fileContent != "":
        await send_result(websocket, {
            "isSuccess": True, 
            "data": {
                "statusType": "paymentStatus",
                "statusCode": _fileContent
            }
        })
    
    return _fileContent



# 啟動 WebSocket Server
print("WebSocket Process Server Start ...")
_setting = config.setting()
if _setting["enableSSL"]:
    print("enableSSL : true")
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    localhost_pem = pathlib.Path(__file__).with_name("server_key.pem")
    ssl_context.load_cert_chain('./app_data/certification/host.crt', './app_data/certification/host.key')

    server_process = websockets.serve(handle_process, port=12002, ssl=ssl_context)
    asyncio.get_event_loop().run_until_complete(server_process)
    asyncio.get_event_loop().run_forever()
else:
    print("enableSSL : false")
    server_process = websockets.serve(handle_process, port=12002)
    asyncio.get_event_loop().run_until_complete(server_process)
    asyncio.get_event_loop().run_forever()


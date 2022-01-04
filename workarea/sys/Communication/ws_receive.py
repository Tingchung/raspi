#!/usr/bin/env python

# Module        : Command WebSocket Server
# Version	    : 1.3
# Last Revise   : 2021/8/19


import asyncio
import datetime
import random
import websockets            
import ssl
import json
import urllib3
import pathlib
from app_code import config 
from app_code import command 


# Service : handle_receive
# Desc : 負責接收前端命令
async def handle_receive(websocket, path):
    print("connecting ...")

    # 載入設定
    _token = config.get_token()
    
    while True:
        # 接收 client 資料
        data = await websocket.recv()

        # 檢查命令內容        
        #   檢查命令格式
        if data == "ack":
            await send_result(websocket, {
                "isSuccess": True, 
                "message": "connection success",
                "statusCode": "CMD-OK-002", 
                "data": data
            })
            continue
        elif data == "comm_conn_test":
            await send_result(websocket, {
                "isSuccess": True, 
                "message": "communication server connection ok", 
                "statusCode": "CMD-OK-003", 
                "data": ""
            })
            continue

        try:
            _command = json.loads(data)
        except ValueError as e:
            await send_result(websocket, {
                "IsSuccess": False, 
                "Message": "wrong command!!", 
                "StatusCode": "CMD-ERR-002", 
                "Data": data
            })
            continue

        #   檢查命令的 token
        if "token" in _command == False:
            await send_result(websocket, {
                "IsSuccess": False, 
                "Message": "token can't be empty!!", 
                "StatusCode": "CMD-ERR-002", 
                "Data": data
            })
            continue

        if _command["token"] != _token:
            await send_result(websocket, {
                "IsSuccess": False, 
                "Message": "token was wrong!!", 
                "StatusCode": "CMD-ERR-003", 
                "Data": data
            })
            continue


        # 寫入命令
        _result = command.add_command(_command)


        # 回覆已接收命令
        await send_result(websocket, {
            "IsSuccess": True, 
            "Message": "", 
            "StatusCode": "CMD-OK-001", 
            "Data": {
                "commandId": _result["data"]["commandId"]
            }
        })
        await asyncio.sleep(0.1)



# Func : send_result
# Desc : 將資料傳送給前端
async def send_result(websocket, thisResult):
    _string_result = json.dumps(thisResult)
    await websocket.send(_string_result)
    print(_string_result)
    return




# 啟動 WebSocket Server
print("WebSocket Receive Server Start ...")
_setting = config.setting()
if _setting["enableSSL"]:
    print("enableSSL : true")
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    localhost_pem = pathlib.Path(__file__).with_name("server_key.pem")
    # ssl_context.load_cert_chain(localhost_pem)
    ssl_context.load_cert_chain('./app_data/certification/host.crt', './app_data/certification/host.key')

    server_receive = websockets.serve(handle_receive, port=12001, ssl=ssl_context)
    asyncio.get_event_loop().run_until_complete(server_receive)
    asyncio.get_event_loop().run_forever()
else:
    print("enableSSL : false")
    server_receive = websockets.serve(handle_receive, port=12001)
    asyncio.get_event_loop().run_until_complete(server_receive)
    asyncio.get_event_loop().run_forever()

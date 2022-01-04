# -*- coding: utf-8 -*-

# Module : process_nccc
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.0
# Last Revise : 2021/8/17


import os
import sys
import json
import time
import config

sys.path.insert(0, config.path('~/../Cuki.DeviceConn.V1/'))
from payment import nccc 



# Func : start_payment
# Desc : 處理 NCCC 刷卡機交易
def start_payment(thisCommandId, thisCommandDetail, thisDeviceInfo):
    # 整理參數
    _commandId = thisCommandId
    _commandDetail = thisCommandDetail
    _deviceInfo = thisDeviceInfo
    _devicePort = "/dev/tty" + _deviceInfo["port"]
    _paymentMethodCode = thisCommandDetail["paymentMethodCode"]
    _totalPrice = int(thisCommandDetail["totalPrice"])


    # 呼叫卡機
    _result = nccc.start_payment(_devicePort, _paymentMethodCode, _totalPrice)
 
    return _result


# Func : send_message
# Desc : 發送 NCCC 刷卡機電文
def send_message(thisCommandId, thisCommandDetail, thisDeviceInfo):
    # 整理參數
    _commandId = thisCommandId
    _commandDetail = thisCommandDetail
    _deviceInfo = thisDeviceInfo
    _devicePort = "/dev/tty" + _deviceInfo["port"]
    _message = _commandDetail["message"]


    # 傳送卡機電文
    _result = {
        "isSuccess": True, 
        "message": "", 
        "data": {
            "statusCode": "", 
            "returnMessage": "000"
        }
    }
    _result = nccc.sendMessage(_devicePort, _message)


    return _result




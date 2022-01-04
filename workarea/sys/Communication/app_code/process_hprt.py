# -*- coding: utf-8 -*-

# Module : process_hprt 漢印
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.0.0
# Last Revise : 2021/9/19


import os
import sys
import json
import time
import config

sys.path.insert(0, config.path('~/../Cuki.DeviceConn.V1/'))
from printer import tp808


# Func : tp808_print
# Desc : 
def tp808_print(thisContent, thisIP):
    # 整理參數
    _content = thisContent
    _IP = thisIP

    try:
        _result_execute = tp808.print_content(_content, _IP)
    except:
        _result_execute = {
            "isSuccess": False,
            "message": "unknow error",
            "data": {
                "statusCode": "tp808-ERR-000"
            }
        }
        
    _result = {
        "statusCode": _result_execute["data"]["statusCode"]
    }

    return _result



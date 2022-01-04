# -*- coding: utf-8 -*-

# Module : process_godex
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.0.10
# Last Revise : 2021/8/26


import os
import sys
import json
import time
import config

sys.path.insert(0, config.path('~/../Cuki.DeviceConn.V1/'))
from printer import dt2x


# Func : dt2x_print
# Desc : 
def dt2x_print(thisContent, thisIP):
    # 整理參數
    _content = thisContent
    _IP = thisIP

    _result_execute = dt2x.print_content(_content, _IP)
    _result = {
        "statusCode": _result_execute["data"]["statusCode"]
    }

    return _result
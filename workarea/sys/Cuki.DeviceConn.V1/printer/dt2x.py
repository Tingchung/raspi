# -*- coding: utf-8 -*-

# Module        : GoDEX DT2X Printer
# Version       : 1.2.12
# Last Revise   : 2021/11/4

import os
import time


# Func : print
# Desc : 列印指定內容
def print_content(thisContent, thisIP, thisPort=9100): 
    # 整理參數
    _content = thisContent
    _ip = thisIP
    _port = thisPort


    result = {
        "isSuccess": False,
        "message": "unknow error",
        "data": {
            "statusCode": "godex-ERR-000"
        }
    }

    try:
        # command = f'echo "{_content}"|nc -q 2 {_ip} {_port}'
        command = f'echo "{_content}"| iconv -f utf-8 -t big5 | nc -q 2 {_ip} {_port}'
        printResult = os.system(command)
        print(printResult)
        
        if (printResult == 0):
            result["isSuccess"] = True
            result["message"]= ""
            result["data"] = {
                "statusCode": "godex-OK-001"
            }
        else: 
            result = {
                "isSuccess": False, 
                "message": "", 
                "data": {
                    "statusCode": "godex-ERR-001"
                }
            }

    except Exception as e:
        message = str(e)
        print('exception: ' + message)

        result["isSuccess"] = False
        result["message"]= message
        result["data"] = {
            "statusCode": "godex-ERR-002"
        }


    return result


if __name__ == "__main__":
    _content = "^Q25,3\n^W35\n^H8\n^P1\n^S4\n^AD\n^C1\n^R0\n~Q+0\n^O0\n^D0\n^E18\n~R255\n^L\nDy2-me-dd\nTh:m:s\nAD,54,34,1,1,0,0E,PRINTER TEST\nBA3,50,82,1,2,80,0,1,12345678\n10\nE"
    print(print_content(_content, f"192.168.25.105"))
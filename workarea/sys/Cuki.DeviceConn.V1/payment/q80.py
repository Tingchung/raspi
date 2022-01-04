# -*- coding: utf-8 -*-

# Module        : Payment.Q80
# Version       : 1.0.0
# Last Revise   : 2021/10/25
# Author        : Johnny Fang <johnnyfang@monkit.tw>
# Support Device Type : Q80





import sys
import os
import serial
import time
import datetime
import math

_FolderPath = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath('{}/../app_code'.format(_FolderPath)))



#=====================================================
#=====[ Device Connection ]===========================
#=====================================================


# Func : send_with_return_dataArray 
# Desc : 傳送電文資料, 並將 EDC 回覆的內容拆解為陣列後回傳
def send_with_return_dataArray(thisPort, thisSendmessage, thisIsConnectTest):
    # 宣告物件
    objSerial = serial.Serial() 
    _Result = {
        "isSuccess": False,
        "message": "",
        "data": {}
    }

    # 設定物件屬性
    objSerial.port = thisPort
    objSerial.baudrate = 9600
    objSerial.bytesize = 8
    objSerial.stopbit = 1
    objSerial.timeout = 1

    # 開啟COMPort
    try:
        objSerial.open()
    except Exception as e:
        print('exception: ' + str(e))

        _Result["isSuccess"] = False
        _Result["message"] = "COMPort open failed"
        _Result["data"] = {
            "statusCode": "NCCC-ERR-003"
        }

        return _Result

    # 檢查 COMPort 是否開啟
    if objSerial.is_open == False:
        _Result["isSuccess"] = False
        _Result["message"] = "COMPort open failed"
        _Result["data"] = {
            "statusCode": "NCCC-ERR-003"
        }

        return _Result

    # 把傳送內容加上開始、結束及LRC
    _Stx = chr(0x02)
    _Etx = chr(0x03)

    _String_Get_LRC = f'{thisSendmessage}{_Etx}'
    _LRC = chr(makeLRC(_String_Get_LRC.encode()))

    if (thisIsConnectTest == True) : 
        _LRC = chr(makeLRC(''.encode()))
    else:  
        _LRC = chr(makeLRC(_String_Get_LRC.encode()))
        
    _String_Send = f'{_Stx}{_String_Get_LRC}{_LRC}'

    print(_String_Send)

    # 發送資料
    objSerial.write(_String_Send.encode())

    # 讀取回應，並判斷第一次是否回兩個 ack
    _Result_ReceiveStatus = objSerial.readline()

    # 檢查回應資料是否正確
    if (len(_Result_ReceiveStatus) <= 0):
        _Result["isSuccess"] = False
        _Result["message"] = "NO Data Return"
        _Result["data"] = {
            "statusCode":  "NCCC-ERR-004"
        }

        return _Result

    _CheckAscII = chr(0x06)
    _String_Check = f'{_CheckAscII}{_CheckAscII}'

    if (_String_Check != _Result_ReceiveStatus.decode()):
        if (thisIsConnectTest == True) :
            print(_Result_ReceiveStatus)
            _Result["isSuccess"] = True
            _Result["message"] = "connected test"
            _Result["data"] = {
                "statusCode":  "NCCC-OK-004"
            }

            return _Result
        else: 
            _Result["isSuccess"] = False
            _Result["message"] = "Data or LRC Error"
            _Result["data"] = {
                "statusCode":  "NCCC-ERR-005"
            }

            return _Result

    time.sleep(0.5)

    # 60 秒內檢查是否有回應
    i = 0
    _String_Transaction = ''

    while i < 60:
        _Result_Transaction = objSerial.readline()

        if (len(_Result_Transaction) > 0):
            _String_Transaction = _Result_Transaction.decode()

            print("Receive Data: " + _String_Transaction)

            objSerial.write(_String_Check.encode())
            break

        time.sleep(1)

        i += 1

    # 關閉 COMPort
    objSerial.close()

    # 判斷是否有內容, 沒有內容代表已 timeout
    if (_String_Transaction == ''):
        _Result["isSuccess"] = False
        _Result["message"] = "EDC Timeout"
        _Result["data"] = {
            "statusCode": "NCCC-ERR-004"
        }

        return _Result

    # 回傳結果
    _edcContent = decompose_receiveContent(_String_Transaction)
    _Result["isSuccess"] = True
    _Result["data"] = {
        "edcContent": _edcContent
    }

    return _Result


# Func : send_with_return_sourceContent 
# Desc : 傳送電文資料, 並直接回傳 EDC 回覆的結果
def send_with_return_sourceContent(thisPort, thisMessage):
    # 宣告物件
    objSerial = serial.Serial() 
    _Result = {
        "isSuccess": False,
        "message": "unknow error",
        "data": {
            "statusCode": "NCCC-ERR-000", 
            "returnMessage": ""
        }
    }

    # 設定物件屬性
    objSerial.port = thisPort
    objSerial.baudrate = 9600
    objSerial.bytesize = 8
    objSerial.stopbit = 1
    objSerial.timeout = 1

    # 開啟COMPort
    try:
        objSerial.open()
    except Exception as e:
        print('exception: ' + str(e))

        _Result["isSuccess"] = False
        _Result["message"] = "COMPort open failed"
        _Result["data"] = {
            "statusCode": "NCCC-ERR-003", 
            "returnMessage": ""
        }

        return _Result

    # 檢查 COMPort 是否開啟
    if objSerial.is_open == False:
        _Result["isSuccess"] = False
        _Result["message"] = "COMPort open failed"
        _Result["data"] = {
            "statusCode": "NCCC-ERR-003", 
            "returnMessage": ""
        }

        return _Result

    # 把傳送內容加上開始、結束及LRC
    _Stx = chr(0x02)
    _Etx = chr(0x03)

    _String_Get_LRC = f'{thisMessage}{_Etx}'
    _LRC = chr(makeLRC(_String_Get_LRC.encode()))

    _String_Send = f'{_Stx}{_String_Get_LRC}{_LRC}'

    print(_String_Send)

    # 發送資料
    objSerial.write(_String_Send.encode())

    # 讀取回應，並判斷第一次是否回兩個 ack
    _Result_ReceiveStatus = objSerial.readline()

    # 檢查回應資料是否正確
    if (len(_Result_ReceiveStatus) <= 0):
        _Result["isSuccess"] = False
        _Result["message"] = "NO Data Return"
        _Result["data"] = {
            "statusCode":  "NCCC-ERR-004", 
            "returnMessage": ""
        }

        return _Result

    _CheckAscII = chr(0x06)
    _String_Check = f'{_CheckAscII}{_CheckAscII}'

    if (_String_Check != _Result_ReceiveStatus.decode()):
        _Result["isSuccess"] = False
        _Result["message"] = "Data or LRC Error"
        _Result["data"] = {
            "statusCode":  "NCCC-ERR-005", 
            "returnMessage": ""
        }

        return _Result
            

    time.sleep(0.5)

    # 60 秒內檢查是否有回應
    i = 0
    _String_Transaction = ''

    while i < 60:
        _Result_Transaction = objSerial.readline()

        if (len(_Result_Transaction) > 0):
            _String_Transaction = _Result_Transaction.decode()

            print("Receive Data: " + _String_Transaction)

            objSerial.write(_String_Check.encode())
            break

        time.sleep(1)

        i += 1

    # 關閉 COMPort
    objSerial.close()

    # 判斷是否有內容, 沒有內容代表已 timeout
    if (_String_Transaction == ''):
        _Result["isSuccess"] = False
        _Result["message"] = "EDC Timeout"
        _Result["data"] = {
            "statusCode": "NCCC-ERR-004", 
            "returnMessage": ""
        }

        return _Result


    # 回傳結果
    _returnMessage = _String_Transaction[1:401]  # 取得內文內容(剔除掉 Stx、Etx、LRC) 
    _Result["isSuccess"] = True
    _Result["message"] = ""
    _Result["data"] = {
        "statusCode": "NCCC-OK-003",
        "returnMessage": _returnMessage
    }

    return _Result


# Func : isConnected
# Desc : 連線測試 (送出錯誤LRC, 回覆為nak 表示可正常收到機器回覆)
def isConnected(thisPort):
    _TransactionType = '01'  # 連線測試

    _String_Content = create_content(_TransactionType, '', 0, '')

    _Result = send(thisPort, _String_Content, True)

    return _Result


# Func : makeLRC 
# Desc : 驗證碼生成
def makeLRC(_message):
    lrc = 0

    for b in _message:
        lrc ^= b

    return lrc


# Func : decompose_receiveContent 
# Desc : 拆解接收資料
def decompose_receiveContent(thisDataString):
    _ReceiveData = [
        thisDataString[1],  # ECR Indicator
        thisDataString[2:8],  # ECR Version Date
        thisDataString[8],  # Trans Type Indicator
        thisDataString[9:11],  # 交易別, 一般交易、取消...etc
        thisDataString[11],  # 交易方式: 信用卡N、S: SmartPay、E: 悠遊卡
        thisDataString[12:14],  # 主機別
        thisDataString[14:20],  # 調閱編號、交易編號
        thisDataString[20:39],  # 卡號
        thisDataString[39:43],  # 信用卡有效期/結帳總筆數
        thisDataString[43:55],  # 交易金額 / 結帳總金額
        thisDataString[55:61],  # 交易日
        thisDataString[61:67],  # 交易時間
        thisDataString[67:76],  # 授權碼
        thisDataString[76],  # Wave Card(Contactless) Indicator
        thisDataString[77:81],  # 通訊回應碼
        thisDataString[81:96],  # EDC商店代號
        thisDataString[96:104],  # EDC端末機代號
        thisDataString[104:116],  # 其他金額(小費)
        thisDataString[116:134],  # 櫃號 (發票號碼)或(櫃號+機號+ECR交易序號)
        thisDataString[134],  # 1全額扣抵, 2部份扣抵, I內含手續費, E外加手續費
        thisDataString[135:147],  # 實際支付金額(含小數2位)
        thisDataString[147:155],  # 信用卡紅利扣抵點數值
        thisDataString[155:163],  # 剩餘紅利
        thisDataString[163:175],  # 折抵金額
        thisDataString[175:177],  # 信用卡分期期數
        thisDataString[177:189],  # 首期金額/電子票證交易前餘額
        thisDataString[189:201],  # 每期金額/電子票證交易後餘額
        thisDataString[201:213],  # 分期手續費/電子票證自動加值金額
        thisDataString[213:215],  # 卡別
        thisDataString[215:221],  # 批次號碼
        thisDataString[221:223],
        thisDataString[223],  # 是否為小額交易(M:是, 空白:否, Y:聯名卡)
        thisDataString[224:232],
        thisDataString[232:240],
        thisDataString[240:252],
        thisDataString[252:257],
        thisDataString[257:307],
        thisDataString[307:313],
        thisDataString[313],
        thisDataString[314],
        thisDataString[315:318],  # 金融機構代碼
        thisDataString[318:323],  # 信用卡保留欄位
        thisDataString[323:401]  # HappyGO連線規格
    ]

    return _ReceiveData



#====================================================
#=====[ Create Content ]=============================
#====================================================


# Func : create_content
# Desc : 產生電文內容
def create_content(thisTransactionType, thisPaymentType, thisTotalPrice, thisApprovalNo):
    _F1 = 'I'  # Indicator m (如果需要用信用卡載具需帶E, 會回傳銀行代碼等相關資料)
    _F2 = produce_space_by_length(6)
    _F3 = produce_space_by_length(1)  # o TransTypeIndicator 可不帶

    _F4 = thisTransactionType  # m 交易類型

    _F5 = produce_space_by_length(1)
    if (thisPaymentType != ''):
        _F5 = thisPaymentType  # m 付款類型

    _F6 = produce_space_by_length(2) 

    _F7 = produce_space_by_length(6)  

    _F8 = produce_space_by_length(19)
    _F9 = produce_space_by_length(4)

    # 交易金額
    _F10 = produce_space_by_length(12)
    if (thisTotalPrice > 0):
        _TotalPrice = get_two_float(round(thisTotalPrice, 2), 2)  # 金額取小數點2位
        _String_TotalPrice = str(_TotalPrice)  # 將金額轉為字串
        _String_TotalPrice = _String_TotalPrice.replace('.', '')  # 去除小數點
        _F10 = _String_TotalPrice.zfill(12)  # 將交易金額補0, 補足長度12

    # 交易日期&時間
    now = datetime.datetime.now()
    _Year = now.strftime('%Y')
    _F11 = _Year[-2:] + now.strftime('%m%d')
    _F12 = now.strftime('%H%M%S')

    _F13 = produce_space_by_length(9)
    if (thisApprovalNo != ''):
        _F13 = thisApprovalNo + \
            produce_space_by_length(9 - len(thisApprovalNo))

    _F14 = produce_space_by_length(1)
    _F15 = produce_space_by_length(4)
    _F16 = produce_space_by_length(15)
    _F17 = produce_space_by_length(8)
    _F18 = produce_space_by_length(12)
    _F19 = produce_space_by_length(18)  # o storeid
    _F20 = produce_space_by_length(1)
    _F21 = produce_space_by_length(12)
    _F22 = produce_space_by_length(8)
    _F23 = produce_space_by_length(8)
    _F24 = produce_space_by_length(12)
    _F25 = produce_space_by_length(2)
    _F26 = produce_space_by_length(12)
    _F27 = produce_space_by_length(12)
    _F28 = produce_space_by_length(12)
    _F29 = produce_space_by_length(2)
    _F30 = produce_space_by_length(6)
    _F31 = produce_space_by_length(2)
    _F32 = produce_space_by_length(1)
    _F33 = produce_space_by_length(8)
    _F34 = produce_space_by_length(8)
    _F35 = produce_space_by_length(12)
    _F36 = produce_space_by_length(5)
    _F37 = produce_space_by_length(50)
    _F38 = produce_space_by_length(6)
    _F39 = produce_space_by_length(1)  # m
    _F40 = produce_space_by_length(1)
    _F41 = produce_space_by_length(3)
    _F42 = produce_space_by_length(5)
    _F43 = produce_space_by_length(78)

    _String_Content = f'{_F1}{_F2}{_F3}{_F4}{_F5}{_F6}{_F7}{_F8}{_F9}{_F10}{_F11}{_F12}{_F13}{_F14}{_F15}{_F16}{_F17}{_F18}{_F19}{_F20}{_F21}{_F22}{_F23}{_F24}{_F25}{_F26}{_F27}{_F28}{_F29}{_F30}{_F31}{_F32}{_F33}{_F34}{_F35}{_F36}{_F37}{_F38}{_F39}{_F40}{_F41}{_F42}{_F43}'

    return _String_Content


# Func : produce_space_by_length
# Desc : 產生欄位所需的空白
def produce_space_by_length(thislength):
    _String_Return = ''

    i = 0
    while i < thislength:
        _String_Return += ' '
        i += 1

    return _String_Return


# Func : get_two_float
# Desc : 強制小數後面補0到指定位數
def get_two_float(f_str, n):
    f_str = str(f_str)
    a, b, c = f_str.partition('.')
    c = (c+"0"*n)[:n]       # 強制小數後面補0到指定位數
    return ".".join([a, c])



#====================================================
#=====[ Business Function ]==========================
#====================================================


# Func : start_payment
# Desc : 發動交易
def start_payment(thisPort, thisPaymentType, thisTotalPrice):
    _TransactionType = '01'  # 一般交易

    _PaymentType = ''
    if thisPaymentType.lower() == 'pay-001':  # 信用卡
        _PaymentType = 'N'

    if thisPaymentType.lower() == 'pay-002':  # 電子票證
        _PaymentType = 'E'

    if thisPaymentType.lower() == 'pay-003':  # 電子支付
        _PaymentType = 'S'

    _String_Content = create_content(
        _TransactionType, _PaymentType, thisTotalPrice, '')

    _Result = send(thisPort, _String_Content, False)

    if _Result['isSuccess'] == False:
        return _Result

    # 取得通訊回應碼, 判斷付款是否成功
    _edcResult = _Result["data"]["edcContent"][14]
    if (_edcResult != "0000"):
        _Result_Payment = {
            "isSuccess": False,
            "message": _edcResult,
            "data": {
                "statusCode": "NCCC-ERR-001",
                "edcContent": _Result["data"]["edcContent"]
            }
        }

        return _Result_Payment

    _Result_Payment = {
        "isSuccess": True,
        "data": {
            "statusCode": "NCCC-OK-001",
            "edcContent": _Result["data"]["edcContent"]
        }
    }

    return _Result_Payment


# Func : start_refund
# Desc : 發動退貨
def start_refund(thisPort, thisPaymentType, thisTotalPrice, thisApprovalNo):
    _TransactionType = '02'  # 退貨

    _PaymentType = ''
    if thisPaymentType.lower() == 'pay-001':  # 信用卡
        _PaymentType = 'N'

    if thisPaymentType.lower() == 'pay-002':  # 電子票證
        _PaymentType = 'E'

    if thisPaymentType.lower() == 'pay-003':  # 電子支付
        _PaymentType = 'S'

    _String_Content = create_content(
        _TransactionType, _PaymentType, thisTotalPrice, thisApprovalNo)

    _Result = send(thisPort, _String_Content, False)

    if _Result['isSuccess'] == False:
        return _Result

    # 取得通訊回應碼, 判斷退款是否成功
    _edcResult = _Result["data"]["edcContent"][14]
    if (_edcResult != "0000"):
        _Result_Payment = {
            "isSuccess": False,
            "message": _edcResult,
            "data": {
                "statusCode": "NCCC-ERR-002",
                "edcContent": _Result["data"]["edcContent"]
            }
        }

    _Result_Payment = {
        "isSuccess": True,
        "data": {
            "statusCode": "NCCC-OK-002",
            "edcContent": _Result["data"]["edcContent"]
        }
    }

    return _Result_Payment





if __name__ == "__main__":
    print(create_content())
    # print(isConnected("/dev/ttyUSB0"))
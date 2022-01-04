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
def send_with_return_dataArray(thisPort, thisSendmessage):
    result = send_with_return_sourceContent(thisPort, thisSendmessage)

    if (result["isSuccess"] == False): 
        return result

    # 回傳結果
    edcReceiveData = decompose_receiveContent(result["data"]["returnMessage"])
    result["isSuccess"] = True
    result["data"] = {
        "statusCode": "Q80-OK-003",
        "edcContent": edcReceiveData
    }

    return result


# Func : send_with_return_sourceContent 
# Desc : 傳送電文資料, 並直接回傳 EDC 回覆的結果
def send_with_return_sourceContent(thisPort, thisMessage):
    # 宣告物件
    objSerial = serial.Serial() 
    result = {
        "isSuccess": False,
        "message": "",
        "data": {}
    }

    # 設定物件屬性
    objSerial.port = thisPort
    objSerial.baudrate = 9600
    objSerial.bytesize = 7
    objSerial.stopbits = 1
    objSerial.timeout = 1
    objSerial.parity = serial.PARITY_EVEN

    # 開啟COMPort
    try:
        objSerial.open()
    except Exception as e:
        print('exception: ' + str(e))

        result["isSuccess"] = False
        result["message"] = "COMPort open failed"
        result["data"] = {
            "statusCode": "Q80-ERR-003"
        }

        return result

    # 檢查 COMPort 是否開啟
    if objSerial.is_open == False:
        result["isSuccess"] = False
        result["message"] = "COMPort open failed"
        result["data"] = {
            "statusCode": "Q80-ERR-003"
        }

        return result

    # 把傳送內容加上開始、結束及LRC
    stx = chr(0x02) 
    etx = chr(0x03)

    #加上etx去產生LRC    
    str_generateLRC = f'{thisMessage}{etx}'
    
    lrc = chr(makeLRC(str_generateLRC))         

    # 組出最後要傳送的結果
    str_send = f'{stx}{str_generateLRC}{lrc}'

    # 發送資料
    objSerial.write(str_send.encode())

    # 讀取回應
    # run 40 秒, 如果回應一直都是空字串, 則表示已 timeout
    i = 0
    receiveStatus = ''
    while i < 40:
        result_receiveStatus = objSerial.readline()

        # 如果已收到回應結果, 則存到變數並離開迴圈
        if (len(result_receiveStatus) > 0):
            receiveStatus = result_receiveStatus.decode()
            break

        time.sleep(1)
        i += 1
    
    # 檢查回應資料是否正確
    # 1. 回傳字串為空, 表示已 timeout 沒有收到回應
    if (len(receiveStatus) <= 0):
        result["isSuccess"] = False
        result["message"] = "NO Data Return"
        result["data"] = {
            "statusCode":  "Q80-ERR-004"
        }

        return result

    # 如果交易類型=連線測試(80)或結帳(50), 因為會直接回覆結果, 不會先回覆2個ack, 所以直接回傳結果
    transactionType = thisMessage[:2] 
    if transactionType == "80" or transactionType =="50":
        # 關閉 COMPort
        objSerial.close()

        # 回傳結果
        _returnMessage = receiveStatus[3:]  # 取得內文內容(剔除掉 Stx、Etx、LRC) 
        result["isSuccess"] = True
        result["message"] = ""
        result["data"] = {
            "statusCode": "Q80-OK-003",
            "returnMessage": _returnMessage
        }

        return result

    # 2. 是否收到2個 ack
    ack = chr(0x06)
    str_checkStatus = f'{ack}{ack}'
    if (str_checkStatus != receiveStatus):
        result["isSuccess"] = False
        result["message"] = "Data or LRC Error"
        result["data"] = {
            "statusCode":  "Q80-ERR-005"
        }

        return result            

    time.sleep(0.5)

    # 60 秒內檢查是否有回應
    i = 0
    str_transaction = ''
    while i < 60:
        result_transaction = objSerial.readline()

        if (len(result_transaction) > 0):
            str_transaction = result_transaction.decode() 

            # 確定有收到回應, 回寫 2 個 ack 給 EDC
            objSerial.write(str_checkStatus.encode())
            break

        time.sleep(1)

        i += 1

    # 關閉 COMPort
    objSerial.close()

    # 判斷是否有內容, 沒有內容代表已 timeout
    if (str_transaction == ''):
        result["isSuccess"] = False
        result["message"] = "EDC Timeout"
        result["data"] = {
            "statusCode": "Q80-ERR-004"
        }

        return result

    # 回傳結果
    _returnMessage = str_transaction[1:601]  # 取得內文內容(剔除掉 Stx、Etx、LRC) 
    result["isSuccess"] = True
    result["message"] = ""
    result["data"] = {
        "statusCode": "Q80-OK-003",
        "returnMessage": _returnMessage
    }

    return result


# Func : isConnected
# Desc : 連線測試 
def isConnected(thisPort):
    _TransactionType = '80'  # 連線測試

    str_Content = create_content(_TransactionType, 0, '')

    result = send_with_return_dataArray(thisPort, str_Content)
    result["data"]["statusCode"] = "Q80-OK-004"

    return result


# Func : makeLRC 
# Desc : 驗證碼生成
def makeLRC(_message):
    lrc = 0

    for b in _message:
        lrc ^= ord(b)
    return lrc


# Func : decompose_receiveContent 
# Desc : 拆解接收資料
def decompose_receiveContent(thisDataString):
    _ReceiveData = [
        thisDataString[:2],  # 1. TransType
        thisDataString[2:4],  # 2. 銀行別
        thisDataString[4:10],  # 3. EDC簽單調閱編號
        thisDataString[10:29],  # 4. 卡號
        thisDataString[29:33],  # 5. 信用卡有效期
        thisDataString[33:45],  # 6. 交易金額
        thisDataString[45:51],  # 7. 交易日期
        thisDataString[51:57],  # 8. 交易時間
        thisDataString[57:66],  # 9. 授權碼
        thisDataString[66:78],  # 10. 分期=首期金額
        thisDataString[78:82],  # 11. 通訊回應碼
        thisDataString[82:90],  # 12. EDC端末機代號
        thisDataString[90:102],  # 13. 銀行交易序號
        thisDataString[102:114],  # 14. 分期=每期金額、紅利=實付金額
        thisDataString[114:132],  # 15. 專櫃號 (StoreID)
        thisDataString[132:134],  # 16. Start Get PAN
        thisDataString[134:137],  # 17. 信用卡和紅利=發卡代號、分期=交易期數
        thisDataString[137],  # 18. 卡片代碼
        thisDataString[138:144],  # 19. 分期=手續費
        thisDataString[144:194],  # 20. 電子發票載具
        thisDataString[194:209],  # 21. 商店代號
        thisDataString[209:215],  # 22. 批次號碼
        thisDataString[215:217],  # 23. 過卡方式
        thisDataString[217:233],  # 24. 晶片碼
        thisDataString[233:273],  # 25. 持卡人名稱
        thisDataString[273],  # 26. 電子票證種類
        thisDataString[274:293],  # 27. 電子票證卡號
        thisDataString[293:303],  # 28. 電子票證交易序號
        thisDataString[303:313],  # 29. 電子票證批次號碼
        thisDataString[313:323],  # 30. 電子票證交易前餘額
        thisDataString[323:333], #31. 電子票證自動加值金額
        thisDataString[333:343],  # 32. 電子票證交易後餘額
        thisDataString[343:359], # 33. 電子票證安全模組編號
        thisDataString[359:369], # 34. 電子票證門市代號
        thisDataString[369:389], # 35. 電子票證錯誤碼
        thisDataString[389:399], # 36. 兌獎用的資料 由自助機印表機列印成QRCode
        thisDataString[399:549], #37. 掃碼資料由自助機帶入刷卡機
        thisDataString[549:551], #38. 掃碼支付業者代碼
        thisDataString[551:571], #39. 掃碼支付業者訂單編號
        thisDataString[571], #40. 不印簽單=>1
        thisDataString[572:],  # 保留欄位
    ]

    return _ReceiveData



#====================================================
#=====[ Create Content ]=============================
#====================================================


# Func : create_content
# Desc : 產生電文內容
def create_content(thisTransactionType, thisTotalPrice, thisApprovalNo):

    _F1 = produce_space_by_length(2)
    if (thisTransactionType != ''):
        _F1 = thisTransactionType  # 交易別
    
    _F2 = produce_space_by_length(2) # 銀行別
    
    _F3 = produce_space_by_length(6)  # InvoiceNO

    _F4 = produce_space_by_length(19)  # 卡號

    _F5 = produce_space_by_length(4) # 卡片效期

    _F6 = produce_space_by_length(12)  
    if (thisTotalPrice > 0):
        _TotalPrice = get_two_float(round(thisTotalPrice, 2), 2)  # 金額取小數點2位
        str_TotalPrice = str(_TotalPrice)  # 將金額轉為字串
        str_TotalPrice = str_TotalPrice.replace('.', '')  # 去除小數點
        _F6 = str_TotalPrice.zfill(12)  # 將交易金額補0, 補足長度12

     # 交易日期&時間
    #now = datetime.datetime.now()
    #_Year = now.strftime('%Y')
    #_F7 =  _Year[-2:] + now.strftime('%m%d')
    #_F8 = now.strftime('%H%M%S')
    _F7 = produce_space_by_length (6)
    _F8 = produce_space_by_length (6)


    _F9 = produce_space_by_length(9) # 授權碼
    if (thisApprovalNo != ''):
        _F9 = thisApprovalNo + \
            produce_space_by_length(9 - len(thisApprovalNo))

    _F10 = produce_space_by_length(12) # 分期=首期金額

    _F11 = produce_space_by_length(4) # 通訊回應碼
    _F12 = produce_space_by_length(8) # EDC端末代號
    _F13 = produce_space_by_length(9) # 銀行交易序號
   

    _F14 = produce_space_by_length(12) # 分期=每期金額、紅利=實付金額
    _F15 = produce_space_by_length(18) #專櫃號
    _F16 = produce_space_by_length(2)  #Start Get PAN  二段式收銀機連線時使用。
    _F17 = produce_space_by_length(3) #信用卡和紅利=發卡代號。 分期=交易期數。
    _F18 = produce_space_by_length(1) #卡片代碼 
    _F19 = produce_space_by_length(6)  # 分期=手續費
    _F20 = produce_space_by_length(50) #電子發票載具 
    _F21 = produce_space_by_length(15) #商店代號(左靠右補空白) 
    _F22 = produce_space_by_length(6) #批次號碼
    _F23 = produce_space_by_length(2) #過卡方式
    _F24 = produce_space_by_length(16) #晶片碼 
    _F25 = produce_space_by_length(40) #持卡人名稱(左靠右補空白) 
    _F26 = produce_space_by_length(1) #電子票證種類
    _F27 = produce_space_by_length(19) #電子票證卡號
    _F28 = produce_space_by_length(10) #電子票證交易序號 
    _F29 = produce_space_by_length(10) #電子票證批次號碼 
    _F30 = produce_space_by_length(10) #電子票證交易前餘額
    _F31 = produce_space_by_length(10) #電子票證自動加值金額 
    _F32 = produce_space_by_length(10) #電子票證交易後餘額
    _F33 = produce_space_by_length(16) #電子票證安全模組編號
    _F34 = produce_space_by_length(10) #電子票證門市代號 
    _F35 = produce_space_by_length(20) #電子票證錯誤碼
    _F36 = produce_space_by_length(10) #兌獎用的資料，由自助機印表機列印成 QRCode。 
    _F37 = produce_space_by_length(150) #掃碼資料由自助機帶入刷卡機 
    _F38 = produce_space_by_length(2) #掃碼支付業者代碼 
    _F39 = produce_space_by_length(20)  # 掃碼支付業者訂單編號
    _F40 = produce_space_by_length(1) #不印簽單 => ‘1’ 
    _F41 = produce_space_by_length(31)

    str_Content = f'{_F1}{_F2}{_F3}{_F4}{_F5}{_F6}{_F7}{_F8}{_F9}{_F10}{_F11}{_F12}{_F13}{_F14}{_F15}{_F16}{_F17}{_F18}{_F19}{_F20}{_F21}{_F22}{_F23}{_F24}{_F25}{_F26}{_F27}{_F28}{_F29}{_F30}{_F31}{_F32}{_F33}{_F34}{_F35}{_F36}{_F37}{_F38}{_F39}{_F40}{_F41}'

    return str_Content


# Func : produce_space_by_length
# Desc : 產生欄位所需的空白
def produce_space_by_length(thislength):
    str_Return = ''

    i = 0
    while i < thislength:
        str_Return += ' '
        i += 1

    return str_Return


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
    transactionType = ''
    if thisPaymentType.lower() == 'pay-001':  # 信用卡
        transactionType = '01'

    if thisPaymentType.lower() == 'pay-002':  # 電子票證
        transactionType = '31' # 悠遊卡

    if thisPaymentType.lower() == 'pay-003':  # 電子支付 (google pay / applepay)
        transactionType = '01'

    str_Content = create_content(
        transactionType, thisTotalPrice, '')
 
    result = send_with_return_dataArray(thisPort, str_Content)

    if result['isSuccess'] == False:
        return result

    # 取得通訊回應碼, 判斷付款是否成功
    _edcResult = result["data"]["edcContent"][10]
    if (_edcResult != "0000"):
        result_Payment = {
            "isSuccess": False,
            "message": _edcResult,
            "data": {
                "statusCode": "Q80-ERR-001",
                "edcContent": result["data"]["edcContent"]
            }
        }

        return result_Payment

    result_Payment = {
        "isSuccess": True,
        "data": {
            "statusCode": "Q80-OK-001",
            "edcContent": result["data"]["edcContent"]
        }
    }

    return result


# Func : edc_checkout
# Desc : 發動結帳
def edc_checkout(thisPort):
    transactionType = '50'

    str_Content = create_content(
        transactionType, 0, '')

    result = send_with_return_dataArray(thisPort, str_Content)

    if result['isSuccess'] == False:
        return result

    # 取得通訊回應碼, 判斷退款是否成功
    _edcResult = result["data"]["edcContent"][10]
    if (_edcResult != "0000"):
        result_Payment = {
            "isSuccess": False,
            "message": _edcResult,
            "data": {
                "statusCode": "Q80-ERR-006",
                "edcContent": result["data"]["edcContent"]
            }
        }

    result_Payment = {
        "isSuccess": True,
        "data": {
            "statusCode": "Q80-OK-005",
            "edcContent": result["data"]["edcContent"]
        }
    }

    return result_Payment





#if __name__ == "__main__":
    #print(create_content())
    # print(isConnected("/dev/ttyUSB0"))
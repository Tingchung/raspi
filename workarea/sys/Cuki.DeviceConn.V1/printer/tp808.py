# -*- coding: utf-8 -*-

# Module        : TP808 Printer
# Version       : 1.0
# Last Revise   : 2021/8/22

import os
import sys
import json

from posixpath import split
from escpos.printer import Network
import base64
import six
import requests


_folderPath = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath('{}/../app_code'.format(_folderPath)))
import config

sys.path.insert(0, config.path('~/../../lib/Cuki.Lib'))
from utility import randomTool


# 圖片快取目錄，檔案路徑
_folderPath_imageCacheList = "~/app_data/file_db/common"
_filePath_imageCacheList = config.path(f"{_folderPath_imageCacheList}/image_cachelist.json")

# 圖片快取路徑
_folderPath_image = "~/app_data/image_temp"


# Func : save_image_by_url
# Desc : 將 url 指定的圖片存下來
def save_image_by_url(thisURL): 
    _url = thisURL
    
    # 取得副檔名
    _urlParamArray = _url.split('?') # 以？切割字串， 取得不含參數的網址
    _urlPathArray = _urlParamArray[0].split("/") #用／切割網址， 取得檔名
    _fileName = _urlPathArray[len(_urlPathArray)-1]
    _fileNameArray = _fileName.split(".") # 用.切割檔名, 取得副檔名
    _subFileName = _fileNameArray[len(_fileNameArray) -1]

    # 取得檔案
    r = requests.get(_url, allow_redirects=True)

    # 檢查目錄是否存在
    _directoryPath = config.path(_folderPath_image)
    if (os.path.exists(_directoryPath) == False): 
        os.mkdir(_directoryPath)

    _id= randomTool.get_id(20)
    _newFileName = f"{_id}.{_subFileName}"
    _filePath = config.path(f"{_folderPath_image}/{_newFileName}")
    open(_filePath, 'wb').write(r.content)
    

    return _newFileName


# Func : get_fileName_from_cacheFile
# Desc : 從快取檔中取得檔案名稱
def get_fileName_from_cacheFile(thisURL):
    _url = thisURL

    # 檢查檔案是否存在
    if (os.path.exists(_filePath_imageCacheList) == False): 
        return ""
    
    # 取得檔案內容， 並確認內容是否為空
    _fileContent = ""
    with open(_filePath_imageCacheList, 'r', encoding="utf-8") as objFile: 
        _fileContent = objFile.read()
    
    if (_fileContent == ""): 
        return ""

    # 檢查快取是否存在
    _imageCacheList = json.loads(_fileContent)
    if (_url.lower() in _imageCacheList): 
        return _imageCacheList[_url.lower()]
    
    return ""


# Func : add_imageCache
# Desc : 將 url 和 檔名存入快取
def add_imageCache(thisURL): 
    _url = thisURL
    _fileName = save_image_by_url(thisURL)

    # 取得圖片快取清單
    _imageCacheList = {}
    if (os.path.exists(_filePath_imageCacheList) == True):
        _fileContent = ""
        with open(_filePath_imageCacheList, 'r', encoding="utf-8") as objFile: 
            _fileContent = objFile.read()

        if (_fileContent != ""): 
            _imageCacheList = json.loads(_fileContent)
    
    
    # 儲存圖片快取清單
    _imageCacheList[_url] = _fileName
    with open(_filePath_imageCacheList, 'w') as objFile: 
        objFile.write(json.dumps(_imageCacheList))

    return True


#Func : produce_invoiceBarcode
#Desc : 處理台灣電子發票的 barcode 
def produce_invoiceBarcode(printer, thisBarcode = ''): 
    ESC = b'\x1b'
    GS = b'\x1d'

    printer._raw(GS+b'\x48\x00')
    printer._raw(GS+b'\x68\x40')
    printer._raw(GS+b'\x77\x01')
    printer._raw(ESC + b'\x61\x01')
    printer._raw(b'\x1d\x6b\x45\x13'+ thisBarcode.encode('utf-8')) 
 

# Func : _fn
def _fn(number):
    return six.int2byte(number)


# Func : _send_2d_code_data
def _send_2d_code_data(printer, fn, cn, data, m=b''):
    """ Wrapper for GS ( k, to calculate and send correct data length.

    :param fn: Function to use.
    :param cn: Output code type. Affects available data.
    :param data: Data to send.
    :param m: Modifier/variant for function. Often '0' where used.
    """
    if len(m) > 1 or len(cn) != 1 or len(fn) != 1:
        raise ValueError("cn and fn must be one byte each.")
    header = printer._int_low_high(len(data) + len(m) + 2, 2)

    printer._raw(b'\x1d' + b'(k' + header + cn + fn + m + data)


# Func : produce_two_qrcode
# Desc : 產生兩個QRCode供列印
def produce_two_qrcode(printer, qrcode_left, qrcode_right, eclevel=0, size=3, model=2,
          native=False, center=False, impl="bitImageRaster"):
    """ Print QR Code for the provided string

    :param content: The content of the code. Numeric data will be more efficiently compacted.
    :param ec: Error-correction level to use. One of QR_ECLEVEL_L (default), QR_ECLEVEL_M, QR_ECLEVEL_Q or
        QR_ECLEVEL_H.
        Higher error correction results in a less compact code.
    :param size: Pixel size to use. Must be 1-16 (default 3)
    :param model: QR code model to use. Must be one of QR_MODEL_1, QR_MODEL_2 (default) or QR_MICRO (not supported
        by all printers).
    :param native: True to render the code on the printer, False to render the code as an image and send it to the
        printer (Default)
    :param center: Centers the code *default:* False
    :param impl: Image-printing-implementation, refer to :meth:`.image()` for details
    """
    # Basic validation
    PAGE_MODE_INIT = b'\x1B\x4C\x1D\x50\x00\xCB\x1B\x57\x00\x00\x00\x00\xA0\x01\xB0\x00\x1B\x54\x00'
    PAGE_MODE_END = b'\x0C'
    PRINT_TEMP = b'\x1D\x28\x6B\x03\x00\x31\x51\x30'

    # Native 2D code printing
    printer._raw(PAGE_MODE_INIT)
    printer._raw(b'\x1b\x24\x40\x00')
    cn = b'1'  # Code type for QR code
    # Select model: 1, 2 or micro.
    _send_2d_code_data(printer, _fn(65), cn, _fn(48 + model) + _fn(0))
    # Set dot size.
    _send_2d_code_data(printer, _fn(67), cn, _fn(size))
    # Set error correction level: L, M, Q, or H
    _send_2d_code_data(printer, _fn(69), cn, _fn(48 + eclevel))
    # Send content & print
    _send_2d_code_data(printer, _fn(80), cn, qrcode_left.encode('utf-8'), b'0')
    _send_2d_code_data(printer, _fn(81), cn, b'', b'0')

    printer._raw(b'\x1b\x24\x00\x01')
    cn = b'1'  # Code type for QR code
    # Select model: 1, 2 or micro.
    _send_2d_code_data(printer, _fn(65), cn, _fn(48 + model) + _fn(0))
    # Set dot size.
    _send_2d_code_data(printer, _fn(67), cn, _fn(size))
    # Set error correction level: L, M, Q, or H
    _send_2d_code_data(printer, _fn(69), cn, _fn(48 + eclevel))
    # Send content & print
    _send_2d_code_data(printer, _fn(80), cn, qrcode_right.encode('utf-8'), b'0')
    _send_2d_code_data(printer, _fn(81), cn, b'', b'0')
    printer._raw(PAGE_MODE_END)


# Func : print_data
# Desc : 列印
def print_content(thisPrintDataList, thisIP):
    _result = {
        "isSuccess": False,
        "message": "unknow error",
        "data": {
            "statusCode": "tp808-ERR-000"
        }
    }

    _ip = thisIP
    _printDataList = thisPrintDataList

    # 宣告印表機物件
    printer = Network(_ip,timeout=1)

    # 先取得所有 Image， 然後存下來
    i = 0
    while(i < len(_printDataList)): 
        _item = _printDataList[i]
        _type = _item["type"].lower()
        _content = _item["content"]
        
        if (_type == "image"): 
            _fileName = get_fileName_from_cacheFile(_content)
            if (_fileName == ""): 
                add_imageCache(_content)
        
        i+=1
       

    # 依傳進來的資料及順序設定及列印資料
    i = 0
    while( i < len(_printDataList)): 
        _item = _printDataList[i]
        _type = _item["type"].lower()
        _content = _item["content"]

        # 設定編碼
        if (_type == "codepage"): 
            printer.codepage =_content

        # 紙張裁切， 內容指定為 part 為部份裁切， 其餘則為完整裁切 
        if (_type == "cut"):
            if (_content.lower() == "part"): 
                printer.cut(mode=_content.upper())
            else: 
                printer.cut()
        
        # 列印文字內容
        if (_type == "text"): 
            printer.text(_content)        

        # 設定文字間距
        if (_type == "line_spacing"): 
            printer.line_spacing(_content)

        # 使用 set function 指定印表機列印的相關樣式
        if (_type == "set"): 
            _data = _content

            _align='left'
            if ("align" in _data): 
                _align = _data["align"]

            _font = 'a'
            if("font" in _data): 
                _font = _data["font"]
            
            _textType = 'normal'
            if("text_type" in _data): 
                _textType = _data["text_type"]
            
            _width=1
            if("width" in _data): 
                _width = _data["width"]

            _height=1
            if("height" in _data): 
                _height = _data["height"]

            _density=9
            if("density" in _data): 
                _density = _data["density"]

            _invert=False
            if("invert" in _data): 
                _invert = _data["invert"]

            _smooth=False
            if("smooth" in _data): 
                _smooth = _data["smooth"]

            _flip=False
            if("flip" in _data): 
                _smooth = _data["flip"] 

            printer.set(align=_align, font=_font, text_type=_textType, width=_width, height=_height, density=_density, invert=_invert, smooth=_smooth, flip=_flip)

        # 使用列印圖片
        if (_type=="image"): 
            _fileName = get_fileName_from_cacheFile(_content)
            _filePath_image = config.path(f"{_folderPath_image}/{_fileName}")
            printer.image(_filePath_image)

        # 使用 _raw 列印 bytearray 內容
        if (_type=="_raw"): 
            # decodeContent = base64.b64decode(_content)
            decodeContent = bytes(_content)
            printer._raw(decodeContent)
        
        # 使用 escpos qrcode function 列印單一 QRCode
        if (_type == "qrcode"): 
            _data = _content

            _qrcode_content = ""
            if ("qrcode_content" in _data): 
                _qrcode_content = _data["qrcode_content"]

            _eclevel = 0
            if ("eclevel" in _data): 
                _eclevel = _data["eclevel"]
            
            _size = 3
            if ("size" in _data): 
                _size = _data["size"]
            
            _model = 2
            if ("model" in _data): 
                _model = _data["model"]
            
            _native = False 
            if ("native" in _data): 
                _native  = _data["native"]

            printer.qr(_qrcode_content, ec=_eclevel, size=_size, model=_model, native=_native)
        
        # 列印 2 個 QRCode（電子發票用）
        if (_type == "two_qrcode"):  
            _data = _content

            # 依 dictionary 內容確認參數的值
            _qrcode_left_content = ""
            if ("qrcode_left_content" in _data):
                _qrcode_left_content = _data["qrcode_left_content"]
            
            _qrcode_right_content = "" 
            if ("qrcode_right_content" in _data): 
                _qrcode_right_content = _data["qrcode_right_content"]
            
            _eclevel = 0
            if ("eclevel" in _data): 
                _eclevel = _data["eclevel"]
            
            _size = 3
            if ("size" in _data): 
                _size = _data["size"]
            
            _model = 2
            if ("model" in _data): 
                _model = _data["model"]
            
            _native = False 
            if ("native" in _data): 
                _native  = _data["native"]
            
            _center = False
            if ("center" in _data): 
                _center = _data["center"]
            
            _impl = "bitImageRaster"
            if ("impl" in _data): 
                _impl = _data["impl"]

            produce_two_qrcode(printer, _qrcode_left_content, _qrcode_right_content, _eclevel, _size , _model, _native, _center, _impl)
        
        # 使用 escpos qrcode function 列印 barcode
        if (_type == "barcode"): 
            _data = _content 

            _barcode_content = "" 
            if ("barcode_content" in _data): 
                _barcode_content = _data["barcode_content"]
            
            _barcodeFormat = ""
            if ("barcode_format" in _data) : 
                _barcodeFormat = _data["barcode_format"]

            _height=64
            if ("height" in _data): 
                _height = _data["height"]
            
            _width=3
            if ("width" in _data): 
                _width = _data["width"]
            
            _pos="BELOW"
            if ("pos" in _data): 
                _pos = _data["pos"]
            
            _font="A"
            if ("font" in _data): 
                _font = _data["font"]
            
            _align_center=True
            if ("align_center" in _data):
                _align_center = _data["align_center"]
            
            _function_type="A"
            if ("function_type" in _data): 
                _function_type = _data["function_type"]

            printer.barcode(_barcode_content,_barcodeFormat, _height, _width, _pos, _font, _align_center, _function_type)
        
        if (_type == "invoice_barcode"): 
            produce_invoiceBarcode(printer, _content)

        i+=1
   
    result = {
        "isSuccess": True,
        "message": "",
        "data": {
            "statusCode": "tp808-OK-001"
        }
    }

    return result 

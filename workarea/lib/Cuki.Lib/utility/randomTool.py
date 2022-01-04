# -*- coding: utf-8 -*-

# Module        : randomTool
# Version       : 1.0.1
# Last Revise   : 2021/9/8
# Author        : Johnny Fang <johnnyfang.tw@gmail.com>


import random
import string
from datetime import datetime


_array = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 
"A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z", 
"a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]



# Func : Get_RandomString
# Desc : 取得一個指定長度、包含數字及英文字母大小寫的隨機字串
def get_randomstring(thisLength):
    '取得指定長度，包含數字及英文字母大小寫的隨機字串'
    _Result = ''
    for i in range(0, thisLength, 1):
        _Code = _array[random.randint(0, 61)]
        _Result += _Code
        
    return _Result


# Func : get_id
# Desc : 取得一個指定長度、包含數字及英文字母大小寫的隨機字串
def get_id(thisLength):
    '''取得一個指定長度的隨機字串'''

    _now = datetime.now()
    _result = _now.strftime("%Y%m%d") + ''.join(random.sample(string.ascii_letters + string.ascii_uppercase + string.digits, thisLength - 8)) 
    
    return _result



if __name__ == '__main__':
    print(get_randomstring(25))
    print(get_id(25))
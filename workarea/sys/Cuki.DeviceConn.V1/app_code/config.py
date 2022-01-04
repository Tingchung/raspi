# -*- coding: utf-8 -*-

# Module : config
# Author : Johnny Fang <johnnyfang.tw@gmail.com>
# Version : 1.0
# Last Revise : 2021/3/10


import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


# Func : path_root 
# Desc : 
def path_root():
    _folderPath_root = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../')
    return _folderPath_root


# Func : path 
# Desc : 
def path(thisPath:str):
    _path = thisPath.replace('~/', path_root() + '/')
    return _path


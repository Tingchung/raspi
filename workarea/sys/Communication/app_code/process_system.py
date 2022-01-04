import json
import os
import sys
import time
import config 


# Func : setting_get_setting 
# Desc : to get the setting file 
def setting_get_setting():
    # check the file is exists or not
    _filePath = config.path("~/app_data/system/setting.json")
    if os.path.exists(_filePath) == False:
        _result = {
            "isSuccess": False, 
            "message": "the setting file is not exist.", 
            "data": {
                "statusCode": "CMD-ERR-110"
            }
        }
        return _result

    # read the setting file
    _setting = config.setting()
    
    # return result 
    _result = {
        "isSuccess": True, 
        "message": "", 
        "data": {
            "statusCode": "CMD-OK-110",
            "setting": _setting
        }
    }
    return _result


# Func : setting_update_setting 
# Desc : to update the setting file 
def setting_update_setting(thisSettingString:str):
    # to process parameters 
    _setting = json.loads(thisSettingString)

    # to check properties
    _propertyNames = ["enableSSL", "printer", "payment"]
    for _propertyName in _propertyNames:
        if _propertyName in _setting == False:
            _result = {
                "isSuccess": False, 
                "message": f"missing property '{_propertyName}'", 
                "data": {
                    "statusCode": "CMD-ERR-111"
                }
            }
            return _result

    # to update the setting file 
    config.update_setting(_setting)


    # return result 
    _result = {
        "isSuccess": True, 
        "message": "", 
        "data": {
            "statusCode": "CMD-OK-111"
        }
    }
    return _result
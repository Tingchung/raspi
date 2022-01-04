# -*- coding: utf-8 -*-

# Module        : TP808 Printer
# Version       : 1.0
# Last Revise   : 2021/8/22

import tp808compact

thisPrintDataList = [
        { "type": "codepage", "content": "big5" },
        { "type": "text", "content": "\n" },
        { "type": "set", "content": { "align": "center", "width": 2, "height": 2 } },
        { "type": "text", "content": "加   點\n" },
        { "type": "set", "content": { "align": "left", "width": 1, "height": 1 } },
        { "type": "text", "content": "訂單 店面\n" },
        { "type": "text", "content": "桌位 1F-A1\n" },
        { "type": "text", "content": "編號 20200101-101010\n" },
        { "type": "text", "content": "時間 2020-01-01 10:10:10\n" },
        { "type": "text", "content": "客戶 過路客\n" },
        { "type": "text", "content": "--------------------------------\n" },
        { "type": "text", "content": "紅茶 去冰,微糖\n" },
        { "type": "text", "content": "               x1\n" },
        { "type": "text", "content": "--------------------------------\n" },
        { "type": "cut", "content": "part" },
        { "type": "invoice", "content": "" }
    ]

# thisPrintDataList = [
#         { "type": "text", "content": "\n1\n\n\n\n\n\n\n\n\n" }
#     ]

thisIP = '10.0.4.115'
tp808compact.print_content(thisPrintDataList,thisIP)
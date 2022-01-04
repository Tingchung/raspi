// Module     : Device devTool JS
// Version      : 1.11.38
// Last Revise  : 2021/12/2

// MyPage Event Flow ::
// MyPage.PrePageLoad -> MyPage.ControlLoad -> MyPage.ControlEvent -> MyPage.PageLoad



// Module : page
var page = {
    timer: {},
    data: {
        "messageTimeOut": 5000, 
        "paymentMethodList": {
            "pay-001": "信用卡",
            "pay-002": "電子票證",
            "pay-003": "電子支付"
        }
    },
    initial: () => {
        label_ip.Text(page.data.websocket);

        // 產生頁面上的刷卡機付款選項
        //      產生支付方式
        var _paymentMethodList = page.data["paymentMethodList"];
        for (iKey in _paymentMethodList) {
            list_paymentMethod.Items.Add({
                Text: MyWeb.Text.Format("{0}, {1}", [iKey, _paymentMethodList[iKey]]),
                Value: iKey
            });
        };
    
        //      取得刷卡機清單
        MyWeb.Ajax.Post({
            Url: "/api",
            Method: "get_setting",
            Param: {},
            Success: (thisResult) => {
                if (thisResult.isSuccess == false) {
                    label_message.Text("取得刷卡機清單資料時發生錯誤!!");
                    setTimeout(() => {
                        label_message.Text("");
                    }, 5000);
                };
    
                // 將清單資料繫結到頁面上
                var _setting = thisResult.data.setting;
                var _paymentList = _setting.payment;
    
                for (var i = 0; i < _paymentList.length; i++) {
                    var _text = MyWeb.Text.Format("{0} : {1} : {2}", [_paymentList[i].port, _paymentList[i].type, _paymentList[i].deviceId]);
                    var _value = _paymentList[i].deviceId;
                    list_paymentDevice.Items.Add({
                        Text: _text,
                        Value: _value
                    });
                };
            }
        });

        // 繫結 WebSocket 連線狀態和 Client Id 到頁面上
        page.timer["conn_check"] = setInterval(() => {
            if (MyWebSocket.Data.IsConnected) {
                label_status_receive.Text("正常");
                label_status_process.Text("正常");
                label_clientId.Text(MyWebSocket.Data.Param["clientId"]);
            } else {
                label_status_receive.Text("unknow");
                label_status_process.Text("unknow");
            };
        }, 1000);
    },
    convert_string_to_bytes: (thisString) => {
        var _string = thisString;
        var _bytes = []; // char codes

        for (var i = 0; i < _string.length; ++i) {
            var _code = _string.charCodeAt(i);
            _bytes = _bytes.concat([_code]);
        }

        return _bytes
    }
};


// Event : MyPage.PrePageLoad
// Desc : 處理頁面前的預先準備程序
MyPage.PrePageLoad(() => {
    // 取得網址參數
    page.data.websocket = MyWeb.Request.UrlParameter("ws");    
    if (page.data.websocket === undefined) {
        page.data.websocket = "wss://192.168.192.100";
    };    
});


// Event : MyPage.ControlEvent
// Desc : 建立頁面控制項的事件函數
MyPage.ControlEvent(() => {
    button_scan_ip.onclick(()=>{
        if(text_scan_ip.Text() == ""){
            return;
        };
        var _ip = text_scan_ip.Text();

        commTool.data["ips"] = [];

        label_message.Text("掃描中 ...");
        commTool.scan_ips(_ip, (thisIPs)=>{
            label_message.Text("區域內的中控機 IP 清單 ： " + JSON.stringify(thisIPs));
            setTimeout(() => {
                label_message.Text("");
            }, 5000);
        });
    });

    // event : button_websocket_conn.OnClick
    // desc : 
    button_websocket_conn.OnClick(()=>{
        // 初始化 Device 物件
        Device.Initial({
            "ws_receive": MyWeb.Text.Format("{0}:12001", [page.data.websocket]),
            "ws_process": MyWeb.Text.Format("{0}:12002", [page.data.websocket])
        });
    });

    // event : button_websocket_disconn.OnClick
    // desc : 
    button_websocket_disconn.OnClick(()=>{
        MyWebSocket.ws_receive.close();
        MyWebSocket.ws_process.close();
    });

    // Event : button_get_setting.OnClick
    // Desc : 取得設定檔
    button_get_setting.OnClick(()=>{
        var _token = document.getElementById("label_token").innerHTML;
        Command.Setting_Get_Setting({
            "token": _token, 
            "callback": () => { }
        });
    });

    // Event : button_update_setting.OnClick
    // Desc : 更新設定檔
    button_update_setting.OnClick(()=>{
        if(text_setting.Text()==""){
            return; 
        };

        var _token = document.getElementById("label_token").innerHTML;
        var _settingString = text_setting.Text();
        Command.Setting_Update_Setting({
            "token": _token, 
            "settingString": _settingString,
            "callback": () => { }
        });
    });

    // event : button_print_to_dt2x.OnClick
    // desc : 
    button_print_to_dt2x.OnClick(() => {
        var _token = document.getElementById("label_token").innerHTML;
        Command.Print_To_DT2X({
            "token": _token,
            "callback": () => { }
        });
    });

    // event : button_print_with_escpos.OnClick
    // desc : 
    button_print_with_escpos.OnClick(()=>{
        var _token = document.getElementById("label_token").innerHTML;
        Command.Print_With_ESCPOS({
            "token": _token,
            "callback": () => { }
        });
    });

    // event : button_print_to_rp700.OnClick
    // desc : 
    button_print_to_rp700.OnClick(()=>{
        Command.Print_To_RP700();
    });

    // Event : button_start_payment.OnClick
    // Desc : 按下 "發動付款" 按鍵
    button_start_payment.OnClick(() => {
        if (text_price.Text() == "") {
            return;
        };

        var _token = document.getElementById("label_token").innerHTML;
        var _deviceId = list_paymentDevice.SelectedItem().Value;
        var _paymentMethodCode = list_paymentMethod.SelectedItem().Value;
        var _orderId = text_orderId.Text();
        var _price = text_price.Text();

        Command.NCCC_Start_Payment({
            "token": _token,
            "deviceId": _deviceId,
            "paymentMethodCode": _paymentMethodCode,
            "orderId": _orderId,
            "totalPrice": _price,
            "callBack": (thisData) => {
                console.log("it's time to call 'Start_Payment', bro");
            }
        });
    });

    // Event :  text_price.OnEnter
    // Desc : 在金額欄按下 Enter
    text_price.OnEnter(() => {
        button_start_payment.Click();
    });

    // Event : button_1.OnClick
    // Desc : 點擊 "DevMode : True (發動模擬付款)" 按鍵
    button_1.OnClick(() => {
        var _StatusCode = text_statusCode.Text();
        Command.DevTest(_StatusCode, true);
    });

    // Event : button_2.OnClick
    // Desc : 點擊 "DevMode : False(發動真實付款)" 按鍵
    button_2.OnClick(() => {
        var _StatusCode = text_statusCode.Text();
        Command.DevTest(_StatusCode, false);
    });

    // Event : button_3.OnClick
    // Desc : 點擊 "取得記錄" 按鍵
    button_3.OnClick(() => {
        var _token = document.getElementById("label_token").innerHTML;
        var _commandId = text_commandId.Text();
        Command.Get_CommandLog({
            "token": _token,
            "commandId": _commandId,
            "callBack": (thisData) => {
            },
            "timeout": () => {
                Device.EventFuncs["ws-ERR-001"]();
            },
            "timeoutSec": 1000
        });
    });

    // Event : button_send_nccc_message.OnClick
    // Desc : 點擊 "發送電文" 按鍵
    button_send_nccc_message.OnClick(() => {
        var _token = document.getElementById("label_token").innerHTML;
        var _message = text_nccc_message.Text();
        Command.NCCC_Send_Message({
            "token": _token,
            "message": _message,
            "callBack": (thisData) => {
                label_message.Text("電文已發送")
                setTimeout(() => {
                    label_message.Text("");
                }, 5000);
            }
        })
    });

    // Event : button_send_nccc_checkout_message.OnClick
    // Desc : 點擊 "發送結帳電文" 按鍵
    button_send_nccc_checkout_message.OnClick(() => {
        var _token = document.getElementById("label_token").innerHTML;
        Command.NCCC_Checkout({
            "token": _token,
            "callBack": (thisData) => {
                label_message.Text("電文已發送")
                setTimeout(() => {
                    label_message.Text("");
                }, 5000);
            }
        });
    });
});


// Event : MyPage.PageLoad
// Desc : 頁面載入時的事件
MyPage.PageLoad(() => {
    // 頁面初始
    page.initial();

    // 註冊事件處理函數
    Device.Register_Events({
        "CMD-OK-110": (thisResult)=>{
            label_message.Text("已取得設定檔內容!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);

            text_setting.Text(JSON.stringify(thisResult["setting"]));
        }, 
        "CMD-ERR-110": (thisResult)=>{
            label_message.Text("取得設定檔內容失敗!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        }, 
        "CMD-OK-111": (thisResult)=>{
            label_message.Text("已更新設定檔內容!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        }, 
        "CMD-ERR-111": (thisResult)=>{
            label_message.Text("更新設定檔內容失敗!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        }, 
        "NCCC-OK-001": (thisResult) => {
            label_message.Text("付款成功!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        },
        "NCCC-OK-003": (thisResult) => {
            // 取得回傳的電文內容並顯示在 console
            var _returnMessage = thisResult["returnMessage"];
            console.log(_returnMessage);

            label_message.Text("NCCC 刷卡機已回傳電文內容, 請查看 console");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);

        },
        "NCCC-ERR-001": (thisResult) => {
            label_message.Text("付款失敗!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        },
        "NCCC-ERR-003": (thisResult) => {
            label_message.Text("NCCC 刷卡機連線異常!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        },
        "NCCC-ERR-005": (thisResult) => {
            label_message.Text("發送的電文內容有誤!!");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        },
        "CMD-OK-100": (thisResult) => {
            var _CommandLog = thisResult["commandLog"];
            console.log(_CommandLog);

            label_message.Text("已取得記錄, 請查看瀏覽器的 console");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        },
        "ws-ERR-001": (thisResult) => {
            alert("與設備控制器的連線已中斷!!");
        },
        "TEST-OK-001": (thisResult) => {
            label_message.Text("自訂狀態碼OK");
            setTimeout(() => {
                label_message.Text("");
            }, page.data["messageTimeOut"]);
        }
    });

    Device.Register_Event("S-ERR-002", () => {
        console.log("websocket connection broken!!");
    });

});


//===========================================================


// Module : Command
// Desc : 用來封裝命令的物件
Command = {
    Setting_Get_Setting: (thisParam)=>{
        _Command = {
            "token": thisParam["token"],
            "commandType": "command",
            "method": "get_setting",
            "expireTimeSpan": 30
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },


    Setting_Update_Setting: (thisParam)=>{
        _Command = {
            "token": thisParam["token"],
            "commandType": "command",
            "method": "update_setting",
            "expireTimeSpan": 30, 
            "settingString": thisParam["settingString"]
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },


    // Func : NCCC_Start_Payment
    // Desc : 發動 NCCC 刷卡機付款程序
    NCCC_Start_Payment: (thisParam) => {
        _Command = {
            "token": thisParam["token"],
            "commandType": "payment",
            "method": "start_payment",
            "expireTimeSpan": 30,
            "deviceId": thisParam["deviceId"],
            "paymentMethodCode": thisParam["paymentMethodCode"],
            "orderId": thisParam["orderId"],
            "totalPrice": thisParam["totalPrice"]
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },


    // Func : NCCC_Send_Message
    // Desc : 發送 NCCC 刷卡機電文
    NCCC_Send_Message: (thisParam) => {
        _Command = {
            "token": thisParam["token"],
            "commandType": "payment",
            "method": "send_message",
            "expireTimeSpan": 30,
            "deviceId": "nccc-001",
            "message": thisParam["message"]
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },


    // Func : NCCC_Checkout
    // Desc : 發送 NCCC 刷卡機結帳電文
    NCCC_Checkout: (thisParam) => {
        _Command = {
            "token": thisParam["token"],
            "commandType": "payment",
            "method": "send_message",
            "expireTimeSpan": 30,
            "deviceId": "nccc-001",
            "message": "I       50                                            210803151547                                                                                                                                                                                                                                                                                                                                              "
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },


    // Func : Get_CommandLog
    // Desc : 取得命令記錄
    Get_CommandLog: (thisParam) => {
        _Command = {
            "token": thisParam["token"],
            "commandType": "command",
            "method": "get_commandlog",
            "expireTimeSpan": 30,
            "commandId": thisParam["commandId"]
        }

        Device.Send_Command(_Command, thisParam["callBack"], thisParam["timeout"], thisParam["timeoutSec"]);
    },


    // Func : Print_To_DT2X
    // Desc : 列印
    Print_To_DT2X: (thisParam) => {
        _Command = {
            "token": thisParam["token"],
            "commandType": "print",
            "method": "print",
            "expireTimeSpan": 30,
            "deviceId": "printer-001",
            "content": "^Q25,3\n^W35\n^H8\n^P1\n^S4\n^AD\n^C1\n^R0\n~Q+0\n^O0\n^D0\n^E18\n~R255\n^L\nDy2-me-dd\nTh:m:s\nAD,54,34,1,1,0,0E,PRINTER TEST\nBA3,50,82,1,2,80,0,1,12345678\n10\nE"
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },


    // Func : Print_With_ESCPOS
    // Desc : 列印
    Print_With_ESCPOS: (thisParam) => {
        _Command = {
            "token": thisParam["token"],
            "commandType": "print",
            "method": "print",
            "expireTimeSpan": 30,
            "deviceId": "printer-002",
            "content": [
                {"type":"codepage", "content": "big5"},
                {"type":"text", "content": "\n"},
                {"type": "image", "content": "https://www.monkit.tw/images/monkit-150.png"},
                {"type":"set", "content": {
                    "align": "center"
                }},
                // {"type": "_raw", "content": page.convert_string_to_bytes("HSER")},
                {"type":"text", "content": "電子發票測試\n"},
                {"type":"text", "content": "110年05-06月\n"},
                {"type":"text", "content": "AB-12340000\n"},
                {"type":"set", "content": {
                    "align": "left"
                }},
                // {"type": "_raw", "content": page.convert_string_to_bytes("HSEA")},
                {"type":"text", "content": "  2021-05-01 22:00:00\n"},
                {"type":"text", "content": "  隨機碼:1234 總計:1000\n"},
                {"type":"text", "content": "  賣方 12345678\n"},
                {"type":"text", "content": "\n"},
                {"type":"cut", "content":"part"}
            ]
        }

        Device.Send_Command(_Command, thisParam["callBack"]);
    },    


    // Func : Print_To_RP700
    // Desc : 列印
    Print_To_RP700: (thisParam)=>{
        Android.Print_To_RP700("http://service.kioskpos.com.tw:8080/receipt/sample");
    }, 


    // Func : DevTest
    // Desc : 開發測試用函數, 可以先用 devMode 來觀察前端的行為是否正確
    DevTest: (thisStatusCode, thisDevMode) => {
        var _token = document.getElementById("label_token").innerHTML;
        var _devReturn = {
            "isSuccess": true,
            "data": {
                "statusCode": thisStatusCode
            }
        };
        _Command = {
            "token": _token,
            "commandType": "payment",
            "method": "start_payment",
            "expireTimeSpan": 30,
            "deviceId": "nccc-001",
            "paymentMethodCode": "pay-001",
            "orderId": "orderId-001",
            "totalPrice": 100,
            "devMode": thisDevMode,
            "devReturn": _devReturn
        };
        Device.Send_Command(_Command, (thisResult) => {
            console.log("dev mode!!");
        });
    }
}
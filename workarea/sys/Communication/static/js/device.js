// Module       : Device JS Library
// Version      : 1.11.45
// Last Revise  : 2021/12/2


//=====[ DataPool ]=================================
// Module : DataPool 
var DataPool = {
    SystemStatusCodeList: []
};



//=====[ MyWebSocket ]=================================
// Module : MyWebSocket 
var MyWebSocket = {
    Data: {
        Url_WebSocket: "",
        IsConnected: false,
        IsOnCommand: false,
        IsTryConn: false,
        TotalRetryConn: 0,
        TotalAckSend: 0
    },
    ws_receive: null,
    ws_process: null,
    Timer_WebSocket: null,
    Timer_ack: null,
    Timer_Check: null,

    // Func : Initial
    Initial: (thisParam) => {
        MyWebSocket.Data.Param = thisParam;
        MyWebSocket.Initial_WebSocket_Conn();
        MyWebSocket.Start_WebSocket_Conn();
    },


    // Func : Start_WebSocket_Conn
    // Desc : 開始進行 WebSocket 連線
    Start_WebSocket_Conn: () => {
        Timer_WebSocket = setInterval(() => {
            if (MyWebSocket.Data.IsTryConn) {
                return;
            };
            if (MyWebSocket.Data.TotalRetryConn >= 3) {
                clearInterval(MyWebSocket.Timer_WebSocket);
                return;
            };
            if (MyWebSocket.Data.IsConnected) {
                clearInterval(MyWebSocket.Timer_WebSocket);
                return;
            } else {
                console.log("try conn : " + MyWebSocket.Data.TotalRetryConn);
                MyWebSocket.Data.IsTryConn = true;
                MyWebSocket.Data.TotalRetryConn += 1;
                MyWebSocket.Initial_WebSocket_Conn();
            };
        }, 40000);
    },


    // Func : Initial_WebSocket_Conn
    // Desc : 初始化 WebSocket 連線
    Initial_WebSocket_Conn: () => {
        var _uri_ws_receive = MyWebSocket.Data.Param.ws_receive;
        var _uri_ws_process = MyWebSocket.Data.Param.ws_process;

        try {
            MyWebSocket.ws_receive = new WebSocket(_uri_ws_receive);
            MyWebSocket.ws_process = new WebSocket(_uri_ws_process);

        } catch (e) {
            MyWebSocket.Data.IsTryConn = false;
            return;
        };
        MyWebSocket.Data.IsTryConn = false;

        // set [ws_process] event function 
        MyWebSocket.ws_process.onopen = () => {
            console.log("ws_send_command is connected.");

            // 發送 ack 以確認連線正確
            MyWebSocket.ws_process.send("ack");

            // 設定各項連線狀態
            MyWebSocket.Data.IsConnected = true;
            MyWebSocket.Data.IsOnCommand = false;
            MyWebSocket.Data.IsTryConn = false;
            MyWebSocket.Data.TotalRetryConn = 0;
        };

        MyWebSocket.ws_process.onmessage = (event) => {
            // 如果是 ws-OK-001 狀態碼就取得並註冊 Client Id
            var _Data = JSON.parse(event.data);
            if ("statusCode" in _Data) {
                if (_Data["statusCode"] == "ws-OK-001") {
                    MyWebSocket.Data.Param["clientId"] = _Data["data"]["clientId"];
                };
            };

            // 設定狀態並呼叫 Proces_Message
            MyWebSocket.Data.IsOnCommand = false;
            MyWebSocket.Process_OnMessage(event.data);
        };

        MyWebSocket.ws_process.onclose = () => {
            MyWebSocket.Data.IsConnected = false;
            MyWebSocket.Start_WebSocket_Conn();
        };

        MyWebSocket.ws_process.onerror = () => {
            MyWebSocket.WebSocket_OnError();
        };


        // set [ws_receive] event function 
        MyWebSocket.ws_receive.onopen = () => {
            console.log("ws_receive is connected.");

            // 發送 ack 以確認連線正確
            MyWebSocket.ws_receive.send("ack");
        };

        MyWebSocket.ws_receive.onmessage = (event) => {
            // 如果是 CMD-OK-001 狀態碼就減少一次 TotalAckSend 
            var _Data = JSON.parse(event.data);
            if ("statusCode" in _Data) {
                if (_Data["statusCode"] == "CMD-OK-002") {
                    MyWebSocket.Data.TotalAckSend -= 1;
                    if (MyWebSocket.Data.TotalAckSend < 0) {
                        MyWebSocket.Data.TotalAckSend = 0;
                    };
                };
            };

            MyWebSocket.Receive_OnMessage(event.data);
        };

        MyWebSocket.ws_receive.onclose = () => {
        };

        MyWebSocket.ws_receive.onerror = () => {
            MyWebSocket.WebSocket_OnError();
        };
    },


    // Event : OnMessage
    // Desc : 資料接收事件
    Receive_OnMessage: (thisData) => { },
    Process_OnMessage: (thisData) => { },
    WebSocket_OnError: () => { },


    // Func : Send_Command
    // Desc : 透過 WebSocket 送出指令
    // Param<thisCommand> : object, 表示要送到 WebSocket 的命令
    Send_Command: (thisCommand) => {
        // 連線及命令執行狀態檢查
        if (MyWebSocket.Data.IsConnected == false) {
            return false;
        };
        if (MyWebSocket.Data.IsOnCommand) {
            return false;
        };
        // MyWebSocket.Data.IsOnCommand = true;

        // 加入 Client Id
        thisCommand["clientId"] = MyWebSocket.Data.Param["clientId"];

        // 將命令物件轉為字串
        var _String_Command = "";
        if (thisCommand == "ack") {
            _String_Command = "ack";
            MyWebSocket.Data.IsOnCommand = false;
        } else {
            _String_Command = JSON.stringify(thisCommand);
        };


        // 送出命令到 WebSocket Receive 頻道
        MyWebSocket.ws_receive.send(_String_Command);
    }
};


// Module : commTool
// Desc : Communication Tool 
var commTool = {
    data: {
        ips: [], 
        totalScan: 0        
    },

    // Func : scan
    // Desc : 
    scan: (thisIP, thisIsEnableSSL) => {
        // 
        var _ip = thisIP;
        var _uri = (thisIsEnableSSL ? "wss" : "ws") + "://" + thisIP + ":12001"

        commTool.data.totalScan += 1;


        // try to connection with websocket
        var objWebSocket = new WebSocket(_uri);

        
        // event : onopen
        // desc : 
        objWebSocket.onopen = () => {
            objWebSocket.send("comm_conn_test");
        };

        // event : onmessage
        // desc : 
        objWebSocket.onmessage = (event) => {
            // 檢查回傳的內容
            // 如果後端回傳 statusCode 並且內容為 CMD-OK-003，表示為中控機
            var _data = JSON.parse(event.data);
            if ("statusCode" in _data) {
                if (_data["statusCode"] == "CMD-OK-003") {
                    if (commTool.data["ips"].includes(_ip) == false) {
                        commTool.data["ips"][commTool.data["ips"].length] = _ip;
                    };
                };
            };

            commTool.data.totalScan -= 1;
            console.log("on message : " + commTool.data.totalScan);
            objWebSocket.close();
        };

        objWebSocket.onerror = (event)=>{
            commTool.data.totalScan -= 1;
            console.log(MyWeb.Text.Format("on error({0}) : {1}", [_ip, commTool.data.totalScan]));
        };
    }, 

    // func : scan_ips
    // desc : 掃描一個 ip 範圍
    scan_ips: (thisIPSection, thisCallBack)=>{
        // 整理準備巡覽的 IP 區段
        var _ipPoints = thisIPSection.split(".");

        // tour the ip array
        var _ip = "";
        for(var i = 1; i < 255; i++){
            _ip = _ipPoints[0] + "." + _ipPoints[1] + "." + _ipPoints[2] + "." + i.toString();
            commTool.scan(_ip);
        };

        // 
        timer_check = setInterval(() => {
            if(commTool.data.totalScan <= 0){
                thisCallBack(commTool.data["ips"]);
                clearInterval(timer_check);
            };
        }, 200);


        return;
    }
};


//=====[ Device ]=================================
// Module : Device 
var Device = {
    data: {
        "allow_autoCheck_webSocket": true,      // 是否允許定時自動檢查 WebSocket 連線, 斷線時會觸發 S-ERR-002 事件
        "ack_timeout": 30000                    // 定時發送 ack 的間隔秒數(毫秒)
    },
    CommandResponse: null,                      // 儲存 WebSocket 回傳的內容
    CommandResponse_CallBack: () => { },        // 當 webSocket 回傳時要呼叫的函數
    CommandResponse_Timeout: () => { },
    CommandReponse_Timeout_Timer: null,
    EventFuncs: {},
    Timers: {},


    // Func : Initial
    Initial: (thisParam) => {
        // 初始化 WebSocket 物件
        //      呼叫 MyWebSocket.Initial 進行初始化
        MyWebSocket.Initial(thisParam);

        //      設定 WebSocket(Receive/Process) 2 個頻道收到訊息時的事件函數
        MyWebSocket.Receive_OnMessage = Device.Receive_OnMessage;
        MyWebSocket.Process_OnMessage = Device.Process_OnMessage;
        MyWebSocket.WebSocket_OnError = () => {
            if ("S-ERR-002" in Device.EventFuncs) {
                Device.EventFuncs["S-ERR-002"]();
            };
        };

        // 設定 ack 的 Timer 物件
        // 定時發送 ack 以測試 WebSocket 連線是否正常
        if (Device.data["allow_autoCheck_webSocket"]) {
            Device.Timers["ack_check"] = setInterval(() => {
                Device.Send_Ack(Device.data["ack_timeout"])
            }, Device.data["ack_timeout"] + 1000);
        };
    },


    // Event : Device.Process_OnMessage
    // Desc : 當接收到 WebSocket "接收命令" 頻道來的資料
    Receive_OnMessage: (thisResult) => {
        Device.CommandResponse = thisResult;

        if (Device.CommandResponse_CallBack != null) {
            clearTimeout(Device.CommandReponse_Timeout_Timer);
            Device.CommandResponse_Timeout = null;

            Device.CommandResponse_CallBack(thisResult);
            Device.CommandResponse_CallBack = null;
        };
    },


    // Event : Device.Process_OnMessage
    // Desc : 當接收到 WebSocket "處理命令" 頻道來的資料
    Process_OnMessage: (thisData) => {
        // 整理回傳資料
        var _result = JSON.parse(thisData);
        var _statusType = _result["statusType"];
        var _statusCode = _result["statusCode"];

        // 依命令處理後的狀態碼呼叫對映的事件函數
        if (_statusCode in Device.EventFuncs) {
            Device.EventFuncs[_statusCode](_result);
        };
    },


    // Func : Send_Command
    // Desc : 送出命令到 WebSocket
    Send_Command: (thisCommand, thisCallBack, thisTimeoutFunc, thisTimeoutSec = 3000) => {
        Device.CommandReponse = null;

        // 設定 callback 函數
        if (thisCallBack != null) {
            Device.CommandResponse_CallBack = thisCallBack;
        } else {
            Device.CommandResponse_CallBack = () => { };
        };

        // 設定 timeout 函數
        if (thisTimeoutFunc != null) {
            Device.CommandResponse_Timeout = thisTimeoutFunc;
            Device.CommandReponse_Timeout_Timer = setTimeout(() => {
                // 當發生 timeout 時, 除了呼叫原先傳入的 timeout 函數, 也一併變更相關系統狀態
                MyWebSocket.Data.IsConnected = false;
                MyWebSocket.Data.IsOnCommand = false;

                // 清空 callback 函數
                Device.CommandResponse_CallBack = null;

                // 執行 timeout 函數
                Device.CommandResponse_Timeout();
            }, thisTimeoutSec); 
        };

        // 送出命令
        MyWebSocket.Send_Command(thisCommand);
    },


    // Func : Send_Ack
    // Desc : 送出 ack 進行 WebSocket 連線測試
    Send_Ack: (thisTimeoutSec = 1000) => {
        Device.Send_Command("ack",
            () => {
                // 這裡是 receive callback 
            },
            () => {
                // 這裡是 receive timeout 
                clearInterval(Device.Timers["ack_check"]);
                console.log("ack_check is cleared!!");

                if ("S-ERR-002" in Device.EventFuncs) {
                    Device.EventFuncs["S-ERR-002"]();
                };
            }, thisTimeoutSec);
    },


    // Func : Register_Events
    // Desc : 註冊事件處理函數
    Register_Events: (thisEventFuncs) => {
        for (var iStatusCode in thisEventFuncs) {
            Device.EventFuncs[iStatusCode] = thisEventFuncs[iStatusCode];
        };
    },


    // Func : Register_Event
    // Desc : 註冊事件處理函數
    Register_Event: (thisStatusCode, thisEventFunc) => {
        Device.EventFuncs[thisStatusCode] = thisEventFunc;
    }
};


//=====[ Android ]===============================
// Module : Android 
var Android = {
    Print_To_RP700: (thisUrl)=>{
        // 呼叫 點餐APP 的列印票據函數
		try {
			window.KPOS.printReceipt(thisUrl);
		} catch (e) {
			console.log("Call kiosk appp 'Print_Receipt' function is fail!!");
		};

		return true;
    }
};
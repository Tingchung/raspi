// Module       : Device Setup JS
// Version      : 1.0.1
// Last Revise  : 2021/10/18



// Event : MyPage.ControlLoad
// Desc : 
MyPage.ControlLoad(()=>{
    
});


// Event : MyPage.ControlEvent
// Desc : 
MyPage.ControlEvent(()=>{
    // Event : button_select_image.OnClick 
    // Desc : 
    button_select_image.OnClick(()=>{
        file_logo.click();
    });

    // Event : file_logo.onchange
    // Desc : 
    file_logo.onchange = ()=>{
        console.log("test upload file");

        objFileLogo = document.getElementById("file_logo");

        MyWeb.Ajax.FileUpload({
            Url: "/api/upload_logo",
            PostData: {
                file: objFileLogo.files[0],
            },
            Success: (thisResult)=> {
                var objImage = document.getElementById("image_logo");
                objImage.src = MyWeb.Text.Format("/static/img/logo.jpg?{0}", [Math.random()]);
            }
        });
    };
});

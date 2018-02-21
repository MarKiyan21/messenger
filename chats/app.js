var token = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MjEzMDA3NzIsImlhdCI6MTUxODcwODc3MiwiaXNzIjoiYXBpLmZsb2N0b3B1cy5jb20iLCJqdGkiOiIxIiwibmJmIjoxNTE4NzA4NzcyLCJzdWIiOiJmbG9jdG9wdXNhcGkifQ.DwGxNSmC4KqULvPWuHOEVF8195x6q5RyQt1s3rtpSLQ";
var key = "53e107177dc00be";
var data = "";
var lng = "ru";
//var channel = "private-5a65a1d874a8d";
var uch = "private-5a65b573d5e5b";
//var uch = "private-5a6247951d3cc";
//var uch = "private-5a65a1d874a8d";
var socket = new WebSocket("ws://localhost:8000/" + uch);

$(document).ready(function() {
//    $.ajax({
//        url: "https://api.floctopus.com/v1/contacts/getlist",
//        type: 'GET',
//        contentType: "application/json",
//        headers: {
//            "Floctopus-Token": token, "Floctopus-Ukey": key
//        },
//        success: function(response) {   
//            console.log(response);}
//    });
    
    $.get("http://localhost:8000/getGroups/", {'uch':uch}, function(response){
        var allGroups = JSON.parse(response);
        
        var listOfGroups = allGroups.map(function(group){
            groupWithoutQuots = replaceQuots(group.name);
            return "<div class='contact' data-name='" + groupWithoutQuots + "' data-pic='" + group.pic + "'  data-channel='" + group.gch + "'><img src='img/" + group.pic + "' alt='logo.png' class='img-circle'><span class='groupName'>" + groupWithoutQuots + "</span></div><br>"
        }).join('');
        
        var div = document.createElement("div");
        div.innerHTML = listOfGroups;

        $('.contactList').append(div);
    });

    $.get("http://localhost:8000/getUsers/", {'uch':uch}, function(response){
        allUsers = JSON.parse(response);
        
        var listOfUsers = allUsers.map(function(user){
            userWithoutQuots = replaceQuots(user.name);
            return "<div class='contact' data-name='" + userWithoutQuots + "' data-pic='" + user.pic + " ' data-channel='" + user.uch + "'><img src='img/" + user.pic + "' alt='avatar.jpg' class='img-circle'><span class='userName'>" + userWithoutQuots + "</span></div><br>"
        }).join('');
        
        var div = document.createElement("div");
        div.innerHTML = listOfUsers;

        $('.contactList').append(div);
        
        var chooseUserList = allUsers.map(function(user){
            userWithoutQuots = replaceQuots(user.name);
            return "<label class='checkbox-inline'><input type='checkbox' class='user' value='" + user.id + "'>" + userWithoutQuots + "</label>"
        }).join('<br>');
        
        var div = document.createElement("div");
        div.innerHTML = chooseUserList;
        
        $('#user-info').append(div);
    });   
});

socket.onopen = function (event) {
    console.log(socket)
    socket.onmessage = function (event) {
        var channel = $('.open-channel').attr('data-channel');
//        alert(channel);
        getMessages(uch, channel);
    }
};

socket.onerror = function (event) {
    console.log(event)
}

socket.onclose = function (event) {
    console.log(event)
}

function getMessages(myCh, chTo) {
    $.ajax({
        url: 'http://localhost:8000/getMessages',
        type: 'get',
        data: {'uch':myCh, 'channel':chTo},
        success: function(response) {
            var messages = JSON.parse(response);
                
            console.log(messages);

            var message = messages.map(function(row, index){
                msgWithoutQuots = replaceQuots(row.msg);
                if (row.from == uch){
                    return "<li class='my-msg' data-msg='" + msgWithoutQuots + "'><div class='msg-text'>" + msgWithoutQuots + "</div></li>"
                } else {
                    return "<li class='other-msg' id='" + index + "' data-msg='" + msgWithoutQuots + "'><div class='msg-text'>" + msgWithoutQuots + "<button type='button' class='btn translate'><i class='fas fa-globe'></i></button></div></li>"
                }
            }).join('');
            
            var field = document.createElement("ul");
            $(field).addClass("chat-flow");
            field.innerHTML = message;
        
            $('.chat-flow').replaceWith(field);
            
            var scrollBottom = Math.max($('.chat-flow').height() - $('.message-field').height(), 0);
            $('.message-field').scrollTop(scrollBottom);
        }
    });
}

function createGroup(e) {
    e.preventDefault();
    
    var users_id = [];
    var name = $("#group-name").val();

    $("input[type=checkbox]:checked").each(function(){
        users_id.push($(this).attr("value"));
    });

    $.ajax({
        url: 'http://localhost:8000/createGroup/',
        type: 'post',
        data: {'id':JSON.stringify(users_id), 'name':name, 'creator':uch},
        success: function(response) {
            info = JSON.parse(response);
            infoWithoutQuots = replaceQuots(info.name);
                
            console.log(info);

            var str = '<div class="contact" data-name="' + infoWithoutQuots + '" data-pic="' + info.pic + '"  data-channel="' + info.gch + '"><img src="img/' + info.pic + '" alt="logo.pic" class="img-circle"><span class="groupName">' + infoWithoutQuots + '</span></div><br>';
        
            var div = document.createElement("div");
            div.innerHTML = str;
        
            $('.contactList').prepend(div);
        }
    });
    document.getElementById("group-form").reset();
    $('#group-name').val('');
    $('#modal-popup').modal('hide')
};

function windowMessages() {
    var newStyle1 = document.createElement("style");
    var style1 = ".message-field {background: url('img/chatbg4.jpg'); border-radius: 5px; width: 98%; height: 100%;}";
    newStyle1.innerHTML = style1;
    document.head.append(newStyle1);
    
    $('.contact').css("background", '#ffffff');
    this.style.background = "#f7f7f7";
    
    var name = $(this).attr("data-name");
    var channel = $(this).attr("data-channel");
    var pic = $(this).attr("data-pic");
    
    var str = '<div class="open-channel" data-channel="' + channel + '"><img src="img/' + pic + '" alt="avatar.jpg" class="img-circle"><span class="userName">' + name + '</span></div>';
    
    var div = document.createElement("div");
    div.innerHTML = str;

    $('.open-channel').replaceWith(div);
    
    getMessages(uch, channel);
    
    $('.form-horizontal').css("visibility", 'visible');
    
}

function replaceQuots(param) {
    withoutQuots = param.replace(/"|'/g, function(match){
        return (match=="'") ? "&apos;" : "&quot;";
    });
    
    return withoutQuots;
}

function translateText() {
    var current = $(this).parent().parent().attr('id');
        var thisText = $(this).parent().parent().attr("data-msg");
        $.ajax({
            url: 'http://localhost:8000/translateMessage/',
            type: 'post',
            data: {'text':thisText, 'language':lng},
            success: function(response) {
                resp = JSON.parse(response);
                text = resp.text
                var field = document.createElement("li");
                $(field).addClass("other-msg");
                field.innerHTML = '<div class="msg-text" style="padding: 7px 8px;"><ins>' + thisText + '</ins><br>' + text + '</div>';
                $('#' + current).replaceWith(field);
            }
        });
}

//chatuploader = new plupload.Uploader({
//				runtimes : 'html5,flash,html4',
//				browse_button : 'chAttach', // you can pass an id...
//				container: document.getElementById('btn-cha-attach'), // ... or DOM Element itself
//				url : '/img/uploadchat',
//				unique_names:true,
//				multi_selection:false,
//				max_file_count: 1,
//			
//				
//				filters : {
//					max_file_size : '64mb',
//					mime_types: [
//						{title : "Image files", extensions : "jpg,gif,png,jpeg"},
//						
//					]
//				},
//			
//				init: {
//					PostInit: function() {
//						
//					},
//			
//					FilesAdded: function(up, files) {
//						
//						swal({
//							title:"Loading...",
//							text:'<div class="progress  progress-striped active" id="progress1" ><div id="progressSlide" style="width: 0%;" class="progress-bar progress-bar-success">Loading...</div></div>',
//							showCancelButton:false,
//							showConfirmButton:false,
//							html: true
//						});
//						
//						up.refresh(); // Reposition Flash/Silverlight
//						chatuploader.start();
//					},
//			
//					UploadProgress: function(up, file) {
//						$("#progressSlide").css('width',file.percent+"%");
//						$("#progress1").data('percent',file.percent+"%");
//					},
//			
//					Error: function(up, err) {
//						
//						swal({
//							title:err.message,
//							text:err.code,
//							type:"error"
//						})
//				
//						up.refresh(); // Reposition Flash/Silverlight
//				
//					},
//					
//					FileUploaded: function(up, file, info) {
//						//swal.close();
//						var obj = JSON.parse(info.response);
//						if(!obj.status){
//							
//							
//						}else{
//						swal({
//							title:"<small>Ready to send</small>",
//							//text:'<img class="img-responsive" src="/chat/'+obj.cleanFileName+'">',
//							imageUrl:"/chat/"+obj.cleanFileName,
//							imageSize:obj.fsize,
//							showCancelButton:true,
//							showConfirmButton:true,
//							confirmButtonText:"Send",
//							html: true
//						},function(isConfirm){
//							
//							if (isConfirm) {
//								
//								var h = obj.height;
//								var m = '<img class="img-responsive" src="/chat/'+obj.prefix+obj.cleanFileName+'">';
//								sendMsg(m,h);
//							}
//							
//						});
//							
//											
//						}
//					
//						
//					}
//				}
//		});	

//		chatuploader.init();





$('#group-form').on("submit", function(e){
    e.preventDefault();
})

$('#close-popup').on("click", function(){
    $('#modal-popup').modal('hide');
    document.getElementById("group-form").reset();
    $('#group-name').val('');
})

$('#form-create-group').on("click", createGroup);

$(document).on("click", ".translate", translateText);

$(document).on("click", ".contact", windowMessages);

$("#send-msg").on("click", function(e) {
    var message = $("#chat-input").val();
    $('#chat-input').val('');
    var channel = $('.open-channel').attr('data-channel');
    var data = {
        msg: message,
        channel: channel,
        uch: uch,
    };
    if (message.trim().length) {
        socket.send(JSON.stringify(data));
        getMessages(uch, channel);
    }
});
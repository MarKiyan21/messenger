var token = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MjEzMDA3NzIsImlhdCI6MTUxODcwODc3MiwiaXNzIjoiYXBpLmZsb2N0b3B1cy5jb20iLCJqdGkiOiIxIiwibmJmIjoxNTE4NzA4NzcyLCJzdWIiOiJmbG9jdG9wdXNhcGkifQ.DwGxNSmC4KqULvPWuHOEVF8195x6q5RyQt1s3rtpSLQ";
var key = "53e107177dc00be";
var data = "";
//var channel = "private-5a65a1d874a8d";
var uch = "private-5a65b573d5e5b";
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
    
    $.get("http://localhost:8000/getGroups/", {uch:uch}, function(response){
        allGroups = JSON.parse(response);
        
        var listOfGroups = allGroups.map(function(group){
            return "<div class='contact' data-name='" + group.name + "' data-pic='" + group.pic + "'  data-channel='" + group.gch + "'><img src='img/" + group.pic + "' alt='logo.png' class='img-circle'><span class='groupName'>" + group.name + "</span></div><br>"
        }).join('');
        
        var div = document.createElement("div");
        div.innerHTML = listOfGroups;

        $('.contactList').append(div);
    });

    $.get("http://localhost:8000/getUsers/", {uch:uch}, function(response){
        allUsers = JSON.parse(response);
        
        var listOfUsers = allUsers.map(function(user){
            return "<div class='contact' data-name='" + user.name + "' data-pic='" + user.pic + " ' data-channel='" + user.uch + "'><img src='img/" + user.pic + "' alt='avatar.jpg' class='img-circle'><span class='userName'>" + user.name + "</span></div><br>"
        }).join('');
        
        var div = document.createElement("div");
        div.innerHTML = listOfUsers;

        $('.contactList').append(div);
        
        var chooseUserList = allUsers.map(function(user){
            return "<label class='checkbox-inline'><input type='checkbox' class='user' value='" + user.id + "'>" + user.name + "</label>"
        }).join('<br>');
        
        var div = document.createElement("div");
        div.innerHTML = chooseUserList;
        
        $('#user-info').append(div);
    });   
});

socket.onopen = function (event) {
    console.log(socket)
    $("#button").on("click", function(e) {
        var message = $("#chat-m").val();
        var data = {
            msg: message,
            channel: channel,
            uch: uch,
        };
        socket.send(JSON.stringify(data));
    });
    socket.onmessage = function (event) {
        alert(event.data);
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
            messages = JSON.parse(response);
                
            console.log(messages);

            var message = messages.map(function(row){
                if (row.from == uch){
                    return "<div class='my-msg pull-right' data-msg='" + row.msg + "'>" + row.msg + "</div><br>"
                } else {
                    return "<div class='other-msg' data-msg='" + row.msg + "'>" + row.msg + "</div><br>"
                }
            }).join('');
        
            var field = document.createElement("div");
            field.innerHTML = message;
        
            $('.message-field').append(field);
        }
    });
}

function createGroup(e) {
    e.preventDefault();
    
    var create = function() {
        var users_id = [];
        var name = $("#group-name").val();

        $("input[type=checkbox]:checked").each(function(){
            users_id.push($(this).attr("value"));
        });

        $.ajax({
            url: 'http://localhost:8000/chat/createGroup',
            type: 'post',
            data: {'id':JSON.stringify(users_id), 'name':name, 'creator':uch},
            success: function(response) {
                info = JSON.parse(response);
                
                console.log(info);

                var str = "<div class='contact' data-name='" + info.name + "' data-pic='" + info.pic + "'  data-channel='" + info.gch + "'><img src='img/" + info.pic + "' alt='logo.pic' class='img-circle'><span class='groupName'>" + info.name + "</span></div><br>";
        
                var div = document.createElement("div");
                div.innerHTML = str;
        
//                $('.contactList').prepend(div);
                $('.contactList').append(div);
            }
        });
        
    }
    create()
    document.getElementById("group-form").reset();
    $('#group-name').val('');
    $('#modal-popup').modal('hide')
};

$('#group-form').on("submit", function(e){
    e.preventDefault();
})

$('#close-popup').on("click", function(){
    $('#modal-popup').modal('hide');
    document.getElementById("group-form").reset();
    $('#group-name').val('');
})

$("#form-create-group").on("click", createGroup);

//$(document).on("click", ".userContact", ".groupContact", function(e){
////    var id = $(this).attr("data-id");
////    var name = $(this).attr("data-name");
////    
////    var str = "<h1 class='dich'>" + name + "</h1>";
////    var h = document.createElement("h1");
////    h.innerHTML = str;  
////    $('.4dich').replaceWith(h);
//    alert($(this).attr("data-name"))
//
//});

$(document).on("click", ".contact", function(e){
    
    var newStyle1 = document.createElement("style");
    var style1 = ".message-field {background: url('img/chatbg4.jpg'); border-radius: 5px; width: 98%; height: 100%;}";
    newStyle1.innerHTML = style1;
    document.head.append(newStyle1);
    
    $('.contact').css("background", '#ffffff');
    this.style.background = "#f7f7f7";
    
    var name = $(this).attr("data-name");
    var channel = $(this).attr("data-channel");
    var pic = $(this).attr("data-pic");
    
    var str = "<div class='open-channel'><img src='img/" + pic + "' alt='avatar.jpg' class='img-circle'><span class='userName'>" + name + "</span></div>";
    
    var div = document.createElement("div");
    div.innerHTML = str;

    $('.open-channel').replaceWith(div);
    
    getMessages(uch, channel);
    
    //ОТРИСОВКА ПОЛЯ ВВОДА!!!

});
var token = "eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MjEzMDA3NzIsImlhdCI6MTUxODcwODc3MiwiaXNzIjoiYXBpLmZsb2N0b3B1cy5jb20iLCJqdGkiOiIxIiwibmJmIjoxNTE4NzA4NzcyLCJzdWIiOiJmbG9jdG9wdXNhcGkifQ.DwGxNSmC4KqULvPWuHOEVF8195x6q5RyQt1s3rtpSLQ";
var key = "53e107177dc00be";
var data = "";
var channel = "private-5a65a1d874a8d";
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
            return "<div class='group-name' data-name='" + group.name + "' data-id='" + group.id + "'<h3><i>Group</i>: " + group.name +"</h3></div>"
        }).join('<br>');
        console.log(listOfGroups);
        var div = document.createElement("div");
        div.innerHTML = listOfGroups;

        $('#groups').append(div);
    });

    $.get("http://localhost:8000/getUsers/", {uch:uch}, function(response){
        allUsers = JSON.parse(response);
        
        var listOfUsers = allUsers.map(function(user){
            return "<label class='checkbox-inline'><input type='checkbox' class='user' value='" + user.id + "'>" + user.name + "</label>"
        }).join('<br>');
        console.log(listOfUsers);
        var div = document.createElement("div");
        div.innerHTML = listOfUsers;
        
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
                data = JSON.parse(response);
                
                console.log(data);

                var str = "<div class='group_name' data='" + data.name + "' value='" + data.id + "'></div>";
        
                var div = document.createElement("div");
                div.innerHTML = str;
        
                $('#groups').unshift(div);
//                $('#groups').append(div);
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

$(document).on("click", ".group-name", function(e){
    var id = $(this).attr("data-id");
    var name = $(this).attr("data-name");
    
    var str = "<h1 class='dich'>" + name + "</h1>";
    var h = document.createElement("h1");
    h.innerHTML = str;  
    $('.dich').replaceWith(h);


});
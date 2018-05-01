import json
import requests
import string, random
from channels import Group
from project.settings import SECRET
from .bot import send_bot

def connect(message):
    message.reply_channel.send({
        "accept": True
    })
    ch = message.content["path"][1:]
    url = 'https://api.floctopus.com/v1/messenger/chat/getuser'
    params = {'ch': ch}
    headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()

    if data['status'] == 1:
        user_id = data['user']['user_id']
        Group(ch).add(message.reply_channel)

        url = 'https://api.floctopus.com/v1/messenger/chat/registerws'
        wsid = str(message.reply_channel)
        params = {'userid': user_id, 'wsid': wsid}
        resp = requests.post(url, data=json.dumps(params), headers=headers)

        url = 'https://api.floctopus.com/v1/messenger/chat/getgroupslist'
        params = {'id': user_id}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if (data['status'] == 1):
            groups = data['groups']
            for gr in groups:
                # if gr['msggroup_type'] == "1":
                # print("CONNECT TO " + str(gr['msggroup_name']))
                Group(gr['msggroup_channel']).add(message.reply_channel)

    else:
        message.reply_channel.send({
            "close": True
        })

def receive(message):
    data = json.loads(message["text"])
    typeOfSocketMsg = data["type"]
    if typeOfSocketMsg == 'correspondence':
        msg = data["msg"]
        gr_id = data["group_id"]
        gr_channel = data["group_channel"]
        user_id = data["user_id"]
        url = 'https://api.floctopus.com/v1/messenger/chat/add/'
        params = {'chto': gr_id, 'chfrom': user_id, 'msg': msg}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)
        data = resp.json()
        last_id = data['id']
        #url = 'https://api.floctopus.com/v1/messenger/chat/changestatus'
        #params = {'id': last_id, 'status': 1}
        #resp = requests.post(url, data=json.dumps(params), headers=headers)
        #data = resp.json()
        #if data['status'] == 1:
        #    status = 1
        #else:
        #    status = 0
        ret = json.dumps({"type":typeOfSocketMsg, "last_id": last_id, "from": user_id, "to": gr_id, "gch": gr_channel, "msg": msg})
        Group(gr_channel).send({
            "text": ret,
        })

    elif typeOfSocketMsg == 'bot':
        msg = data["msg"]
        gr_id = data["group_id"]
        gr_channel = data["group_channel"]
        user_id = data["user_id"]
        uch = data["uch"]
        send_bot(msg, gr_id, gr_channel, user_id, uch)

    elif typeOfSocketMsg == "create":
        groupName = data['name']
        pic = data['pic']
        creator = data['creator']
        users = json.loads(data['users'])
        groupName = groupName if groupName else "Group"
        groupChannel = "group-" + ''.join(random.sample(string.ascii_lowercase + string.digits, k=13))

        url = 'https://api.floctopus.com/v1/messenger/chat/addgroup'
        params = {'name': groupName, 'creator': creator, 'channel': groupChannel, 'members': users}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)
        dataResponse = resp.json()

        if dataResponse['status'] == 1:
            groupId = dataResponse['id']
            userName = dataResponse['user_name']

            for ws in dataResponse['websockets']:
                Group(groupChannel).add(ws['ws_reply_channel'])

            msg = userName + ' created the group "' + groupName + '"'
            url = 'https://api.floctopus.com/v1/messenger/chat/add/'
            params = {'chto': groupId, 'chfrom': 0, 'msg': msg}
            headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
            resp = requests.post(url, data=json.dumps(params), headers=headers)

            ret = json.dumps({"type": typeOfSocketMsg, "from": 0, "to": groupId, "msg": msg, "name": groupName, "gch": groupChannel, "pic": pic, "creator": creator})
            Group(groupChannel).send({
                "text": ret,
            })

    elif typeOfSocketMsg == "rename":
        userId = data['user_id']
        groupId = data['group_id']
        groupChannel = data['group_channel']
        newName = data['name']
        url = 'https://api.floctopus.com/v1/messenger/chat/grouprename'
        params = {'name': newName, 'groupid': groupId, 'userid': userId}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)
        dataResponse = resp.json()

        if dataResponse['status'] == 1:
            userName = dataResponse['user_name']

            msg = userName + ' renamed the group to "' + newName + '"'
            url = 'https://api.floctopus.com/v1/messenger/chat/add/'
            params = {'chto': groupId, 'chfrom': 0, 'msg': msg}
            headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
            resp = requests.post(url, data=json.dumps(params), headers=headers)
            data = resp.json()
            last_id = data['id']

            ret = json.dumps({"type": typeOfSocketMsg, "last_id": last_id, "from": 0, "to": groupId, "gch": groupChannel, "msg": msg, "name": newName})
            Group(groupChannel).send({
                "text": ret,
            })

    elif typeOfSocketMsg == "leave":
        userId = data['user_id']
        groupId = data['group_id']
        groupChannel = data['group_channel']

        url = 'https://api.floctopus.com/v1/messenger/chat/leavegroupmember'
        params = {'groupid': groupId, 'members': userId}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)
        dataResponse = resp.json()

        if dataResponse['status'] == 1:

            names = []
            for name in dataResponse['names']:
                names.append(name['user_name'])
            msg = ', '.join(names[:])
            msg += ' left group'
            url = 'https://api.floctopus.com/v1/messenger/chat/add/'
            params = {'chto': groupId, 'chfrom': 0, 'msg': msg}
            headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
            resp = requests.post(url, data=json.dumps(params), headers=headers)
            data = resp.json()
            last_id = data['id']

            ret = json.dumps({"type": typeOfSocketMsg, "last_id": last_id, "from": 0, "to": groupId, "gch": groupChannel, "msg": msg})
            Group(groupChannel).send({
                "text": ret,
            })

            for ws in dataResponse['websockets']:
                Group(groupChannel).discard(ws['ws_reply_channel'])

            for ch in dataResponse['channels']:
                Group(ch).send({
                    "text": json.dumps({"type": "exclude", "to": groupId, "who": ws['ws_user_id'], "gch": groupChannel , "grid": groupId}),
                })

    elif typeOfSocketMsg == "remove":
        userId = data['user_id']
        groupId = data['group_id']
        groupChannel = data['group_channel']

        url = 'https://api.floctopus.com/v1/messenger/chat/removegroup'
        params = {'groupid': groupId}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)
        dataResponse = resp.json()

        if dataResponse['status'] == 1:

            for ws in dataResponse['websockets']:
                Group(groupChannel).discard(ws['ws_reply_channel'])

            for ch in dataResponse['channels']:
                Group(ch).send({
                    "text": json.dumps({"type": "exclude", "to": groupId, "who": ws['ws_user_id'], "gch": groupChannel , "grid": groupId}),
                })

    elif typeOfSocketMsg == "add":
        users = json.loads(data['users_id'])
        if users:
            groupId = data['group_id']
            groupName = data['group_name']
            groupPic = data['group_pic']
            groupChannel = data['group_channel']
            creator = data['creator']

            url = 'https://api.floctopus.com/v1/messenger/chat/addgroupmember'
            params = {'groupid': groupId, 'members': users}
            headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
            resp = requests.post(url, data=json.dumps(params), headers=headers)
            dataResponse = resp.json()

            if dataResponse['status'] == 1:

                for ws in dataResponse['websockets']:
                    Group(groupChannel).add(ws['ws_reply_channel'])

                names = []
                for name in dataResponse['names']:
                    names.append(name['user_name'])
                msg = ', '.join(names[:])
                msg += ' connected to group'
                url = 'https://api.floctopus.com/v1/messenger/chat/add/'
                params = {'chto': groupId, 'chfrom': 0, 'msg': msg}
                headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
                resp = requests.post(url, data=json.dumps(params), headers=headers)
                data = resp.json()
                last_id = data['id']

                ret = json.dumps({"type": typeOfSocketMsg, "last_id": last_id, "from": 0, "to": groupId, "msg": msg, "name": groupName, "gch": groupChannel, "pic": groupPic, "creator": creator})
                Group(groupChannel).send({
                    "text": ret,
                })

    elif typeOfSocketMsg == "connect":
        groupChannel = data['group_channel']
        groupId = data['group_id']
        userChannel = data['user_channel']
        userId = data['user_id']
        userName = data['name']
        userPic = data['pic']
        userWs = data['ws']
        myWs = data['myws']

        Group(groupChannel).add(userWs)
        Group(groupChannel).add(myWs)

        ret = json.dumps({"type":typeOfSocketMsg, "gch": groupChannel, "gid": groupId, "uid": userId, "name": userName, "pic": userPic})
        Group(userChannel).send({
            "text": ret,
        })

    # Переробити, коли буде API для бота #
    #if channel == "floctoid":
        #send_bot(msg, uch)
    #else:

    #    chat = Chats(chat_from=uch, chat_to=channel, chat_msg=msg)
    #    chat.save()
    #    last_id = Chats.objects.latest('chat_id').chat_id
    # ret = json.dumps({"id": last_id, "from": uch, "msg": msg, "status": 1})
    # ret = json.dumps("msg": msg})
    # Group(channel).send({
    #     "text": msg,
    # })

def disconnect(message):
    ch = message.content["path"][1:]
    url = 'https://api.floctopus.com/v1/messenger/chat/getuser'
    params = {'ch': ch}
    headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    if data['status'] == 1:
        user_id = data['user']['user_id']
        url = 'https://api.floctopus.com/v1/messenger/chat/getgroupslist'
        params = {'id': user_id}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if (data['status'] == 1):
            groups = data['groups']
            for gr in groups:
                # print("DISCARD FROM " + str(gr['msggroup_name']))
                Group(gr['msggroup_channel']).discard(message.reply_channel)
    Group(ch).discard(message.reply_channel)


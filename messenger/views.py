import json
import string, random
import MySQLdb
from channels import Group
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt
from project import settings
from googletrans import Translator

from .models import Groups, GroupMembers

def chat(request):
    return render(request, 'base.html')

def getUsers(request):
    uch = request.GET.get('uch')
    array = []
    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT user_id, user_name, user_pic, user_pusher_channel from users WHERE user_pusher_channel!='{}'".format(uch))
    for tpl in cursor:
        array.append({"id": tpl[0], "name": tpl[1], "pic": "avatar2x50.jpg", "uch": tpl[3]})
    cursor.close()
    db.close()

    array = json.dumps(array)
    return HttpResponse(array)

def getGroups(request):
    uch = request.GET.get('uch')
    array = []
    group_id = []
    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM users WHERE user_pusher_channel='{}'".format(uch))
    columns = cursor.fetchone()
    user_id = columns[0]
    cursor.execute("SELECT gr_mem_id_group FROM group_members WHERE gr_mem_id_user='{}'".format(user_id))
    for tpl in cursor:
        group_id.append(tpl[0])
    for i in group_id:
        cursor.execute("SELECT * FROM groups WHERE groups_id='{}'".format(i))
        for tpl in cursor:
            array.append({"id": i, "name": tpl[1], "creator": tpl[2], "gch":tpl[3], "pic":"nologo.png"})

    cursor.close()
    db.close()

    array = json.dumps(array)
    return HttpResponse(array)

def getMessages(request):
    uch = request.GET.get('uch')
    channel = request.GET.get('channel')
    pre = channel.split('-')
    array = []

    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()

    if (pre[0] == 'group'):
        cursor.execute("(SELECT * FROM chats WHERE chat_to='{}' ORDER BY chat_id DESC LIMIT 0, 30) ORDER BY chat_id ASC".format(channel))
    else:
        cursor.execute("(SELECT * FROM chats WHERE (chat_from='{}' AND chat_to='{}') OR (chat_to='{}' AND chat_from='{}') ORDER BY chat_id DESC LIMIT 0, 30) ORDER BY chat_id ASC".format(uch, channel, uch, channel))
    
    for tpl in cursor:
        array.append({"from": tpl[1], "to": tpl[2], "msg": tpl[4]})

    cursor.close()
    db.close()

    array = json.dumps(array)
    return HttpResponse(array)

@csrf_exempt
def createGroup(request):
    ids = json.loads(request.POST.get('id'))
    name = request.POST.get('name')
    name = name if name else "Group"
    creator = request.POST.get('creator')
    secret = "group-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=13))

    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()

    group = Groups(groups_name=name, groups_creator=creator, groups_channel=secret)
    group.save()
    group_id = Groups.objects.latest('groups_id').groups_id

    ret = json.dumps({"id":group_id, "name":name, "gch":secret, "pic":"nologo.png"})

    cursor.execute("SELECT user_id FROM users WHERE user_pusher_channel='{}'".format(creator))
    columns = cursor.fetchone()
    creator_id = columns[0]
    group_mem = GroupMembers(gr_mem_id_group=group_id, gr_mem_id_user=creator_id)
    group_mem.save()

    for i in ids:
        group_mem = GroupMembers(gr_mem_id_group=group_id, gr_mem_id_user=i)
        group_mem.save()

    for i in ids:
        cursor.execute("SELECT ws_reply_channel FROM websockets WHERE ws_user_id='{}'".format(i))
        for tpl in cursor:
            Group(secret).add(tpl[0])
    cursor.close()
    db.close()

    return HttpResponse(ret)

@csrf_exempt
def translateMessage(request):
    translator = Translator()
    text = request.POST.get('text')
    ln = request.POST.get('language')

    currLang = translator.detect(text).lang

    if currLang != ln:
        text = translator.translate(text, dest=ln).text

    ret = json.dumps({'text':text, 'language':ln})

    return HttpResponse(ret)

# @csrf_exempt
# def deleteGroup(request):
#     secret = request.POST.get('secret')
#     db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
#     cursor = db.cursor()
#     cursor.execute("SELECT ws_reply_channel FROM websockets WHERE ws_user_id='{}'".format(i))
#     for tpl in cursor:
#         Group(secret).add(tpl[0])
#     cursor.close()
#     db.close()
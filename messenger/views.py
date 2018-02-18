import json
import string, random
import MySQLdb
from channels import Group
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt
from project import settings

from .models import Groups, GroupMembers

def chat(request):
    return render(request, 'base.html')

def getUsers(request):
    uch = request.GET.get('uch')
    array = []
    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT user_id, user_name, user_pic from users WHERE user_pusher_channel!='{}'".format(uch))
    for tpl in cursor:
        array.append({"id": tpl[0], "name": tpl[1], "pic": tpl[2]})
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
        cursor.execute("SELECT groups_name FROM groups WHERE groups_id='{}'".format(i))
        for tpl in cursor:
            array.append({"id": i, "name": tpl[0]})

    cursor.close()
    db.close()

    array = json.dumps(array)
    return HttpResponse(array)

@csrf_exempt
def createGroup(request):
    ids = json.loads(request.POST.get('id'))
    name = request.POST.get('name')
    creator = request.POST.get('creator')
    secret = "group-" + ''.join(random.choices(string.ascii_lowercase + string.digits, k=13))

    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()

    group = Groups(groups_name=name if name else "Group", groups_creator=creator, groups_channel=secret)
    group.save()
    group_id = Groups.objects.latest('groups_id').groups_id

    ret = json.dumps({"id":group_id, "name":name, "ids":ids})

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

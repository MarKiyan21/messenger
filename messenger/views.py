import json
import MySQLdb
from django.shortcuts import HttpResponse, render
from django.views.decorators.csrf import csrf_exempt
from project import settings

def chat(request):
    return render(request, 'base.html')

def getUsers(request):
    ret = {}
    index = 0
    db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT user_name from users")
    for tpl in cursor:
        for elem in tpl:
            ret[index] = elem
            index += 1
    cursor.close()
    ret = json.dumps(ret)
    return HttpResponse(ret)
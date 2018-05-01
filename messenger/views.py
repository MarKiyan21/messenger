import json
import requests
import string, random
from channels import Group
from googletrans import Translator
from project.settings import SECRET
from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def createGroup(request):
    ret = []
    ids = json.loads(request.POST.get('ids'))
    name = request.POST.get('name')
    creator_id = request.POST.get('creator')
    name = name if name else "Group"
    secret = "group-" + ''.join(random.sample(string.ascii_lowercase + string.digits, k=13))

    url = 'https://api.floctopus.com/v1/messenger/chat/addgroup'
    params = {'name': name, 'creator': creator_id, 'channel': secret, 'members': ids}
    headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
    resp = requests.post(url, data=json.dumps(params), headers=headers)
    data = resp.json()

    if data['status'] == 1:
        group_id = data['id']
        ret = json.dumps({"group_id":group_id, "name":name, "gch":secret, "pic":"nologo.png"})

        for i in data['websockets']: 
            Group(secret).add(i['ws_reply_channel'])
            print(i['ws_reply_channel'])

        msg = 'Group "' + name + '" created'
        url = 'https://api.floctopus.com/v1/messenger/chat/add/'
        params = {'chto': group_id, 'chfrom': 0, 'msg': msg}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)

        # if data['status'] == 1:
        #     ret_create_gr = json.dumps({"id": last_id, "from": secret, "to": "allgroupmem", "msg": msg, "status": 1, "name":name, "gch":secret, "pic":"nologo.png"})
        #     Group(secret).send({
        #         "text": ret_create_gr,
        #     })

    return HttpResponse(ret)

def getGroups(request):
    user_id = request.GET.get('id')
    array = []
    url = 'https://api.floctopus.com/v1/messenger/chat/getgroupslist'
    params = {'id': user_id}
    headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    if data['status'] == 1:
        for group in data['groups']:
            array.append({"id": group['msggroup_id'], "name": group['msggroup_name'], "creator": group['msggroup_user_id'], "gch": group['msggroup_channel'], "pic": "nologo.png"})

    array = json.dumps(array)
    return HttpResponse(array)

@csrf_exempt
def translateMessage(request):
    translator = Translator()
    text = request.POST.get('text')
    ln = request.POST.get('language')

    currLang = translator.detect(text).lang

    if currLang != ln:
        text = translator.translate(text, dest=ln).text

    ret = json.dumps({'text':text, 'language':ln, 'curLang':currLang})
    return HttpResponse(ret)

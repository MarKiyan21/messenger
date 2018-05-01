import json
import requests
from channels import Group
from django.conf import settings
from project.settings import SECRET

import time

class Handle(object):

    def __init__(self, channel, gr_id, user_id, uch, msg):
        self.subj_id = 0
        self.act_id = 0
        self.channel = channel
        self.msg = msg
        self.uch = uch
        self.gr_id = gr_id
        self.user_id = user_id
        self.last_id = 0
        self.bad_answer = "Actually, I don't unserstand you."

    def save_to_chat(self, ch_from, ch_to):
        url = 'https://api.floctopus.com/v1/messenger/chat/add/'
        params = {'chto': ch_to, 'chfrom': ch_from, 'msg': self.msg}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)
        data = resp.json()
        self.last_id = data['id']

    def save_to_train_data(self, quest, answ):
        url = 'https://api.floctopus.com/v1/messenger/chat/addtraindata'
        params = {'userid': self.user_id, 'q': quest, 'a': answ}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.post(url, data=json.dumps(params), headers=headers)

    def push_socket(self, message):
        ret = json.dumps({"type":"correspondence", "last_id": self.last_id, "from": "-1", "to": self.gr_id, "gch": self.channel, "msg": message})
        Group(self.channel).send({
            "text": ret,
        })

    def handle_greeting(self):
        url = 'https://api.floctopus.com/v1/messenger/chat/getuser'
        params = {'ch': self.uch}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if data['status'] == 1:
            name = data['user']['user_name']
            self.msg = "Hello, mr. {}!".format(name)
            self.save_to_chat("-1", self.gr_id)
            self.push_socket(self.msg)

    def handle_confirmation(self, confirm):
        url = 'https://api.floctopus.com/v1/messenger/chat/getlasttdbyuserid'
        params = {'userid': self.user_id}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        answ_id = 'none'
        if data['status'] == 1:
            answ_id = data['td']['train_id']
            answ_check = data['td']['train_give_answ']

        if answ_check == '0':
            self.msg = "Thank you!"
            if confirm == 'no' or confirm == 'n':
                result = 0
            else:
                result = 1
            url = 'https://api.floctopus.com/v1/messenger/chat/updatetraindata'
            params = {'tdid': answ_id, 'result': result}
            headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
            resp = requests.post(url, data=json.dumps(params), headers=headers)
        else:
            self.msg = self.bad_answer

        self.save_to_chat("-1", self.gr_id)
        self.push_socket(self.msg)

    def handle_answer(self, question):
        if self.subj_id != 0:
            self.push_socket("I think you will find this information in")
            if self.act_id == 0:
                self.msg = "http://help.floctopus.com/articles/?cat={}".format(self.subj_id)
            else:
                self.msg = "http://help.floctopus.com/articles/view/{}".format(self.act_id)
        else:
            self.msg = self.bad_answer

        self.save_to_chat("-1", self.gr_id)
        self.push_socket(self.msg)

        if self.msg != self.bad_answer:
            self.save_to_train_data(question, self.msg)
            self.msg = "Tell me, please, this information was useful for you? Yes or No?"

            self.save_to_chat("-1", self.gr_id)
            self.push_socket(self.msg)

    def find_similar_question(self, question):
        url = 'https://api.floctopus.com/v1/messenger/chat/getsamequestion'
        params = {'q': self.msg}
        headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
        resp = requests.get(url, params=params, headers=headers)
        data = resp.json()
        if data['status'] == 1:
            self.push_socket("I think you will find this information in")
            self.msg = data['td']['train_answer']
            self.save_to_chat("-1", self.gr_id)
            self.push_socket(self.msg)
            self.save_to_train_data(question, self.msg)

            self.msg = "Tell me, please, this information was useful for you? Yes or No?"

            self.save_to_chat("-1", self.gr_id)
            self.push_socket(self.msg)

            return True
        else:
            return False

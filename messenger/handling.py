import json
import MySQLdb
from channels import Group
from django.conf import settings

from .models import Chats
from .models import TrainingData

import time

class Handle(object):

    def __init__(self, channel, msg, uch):
        self.subj_id = 0
        self.act_id = 0
        self.channel = channel
        self.msg = msg
        self.uch = uch
        self.last_id = 0
        self.bad_answer = "Actually, I don't unserstand you."
        self.db = MySQLdb.connect(host=settings.MYSQL_HOST, user=settings.MYSQL_USER, passwd=settings.MYSQL_PASSWD, db=settings.MYSQL_NAME)

    def save_to_chat(self, ch_from, ch_to):
        chat = Chats(chat_from=ch_from, chat_to=ch_to, chat_msg=self.msg)
        chat.save()
        self.last_id = Chats.objects.latest('chat_id').chat_id
        
    def save_to_train_data(self, quest, answ, user):
        training = TrainingData(train_question=quest, train_answer=answ, train_user_id=user)
        training.save()
        
    def accessing_to_database(self, mysql_req, update=False):
        cursor = self.db.cursor()
        cursor.execute(mysql_req)
        if update:
            self.db.commit()
            cursor.close()
        else:
            columns = cursor.fetchone()
            cursor.close()
            return columns

    def push_socket(self, push_from, push_to, msg):
        ret = json.dumps([{"id": self.last_id}, {"from": push_from}, {"msg": msg}, {"status": 0}])
        Group(push_to).send({
            "text": ret
        })

    def handle_greeting(self):
        columns = self.accessing_to_database("SELECT * FROM users WHERE user_pusher_channel='{}'".format(self.uch))
        name = columns[6]
        self.msg = "Hello, mr. {}!".format(name)
        self.save_to_chat(self.channel, self.uch)
        self.push_socket(self.channel, self.uch, self.msg)

    def handle_confirmation(self, confirm):
        columns = self.accessing_to_database("SELECT * FROM users WHERE user_pusher_channel='{}'".format(self.uch))
        user_id = columns[0]
        columns = self.accessing_to_database("SELECT * FROM training_data WHERE train_user_id={} ORDER BY train_id DESC LIMIT 1".format(user_id))
        answ_id = columns[0]
        answ_check = columns[6]

        if answ_check == 0:
            self.msg = "Thank you!"
            if confirm == 'no' or confirm == 'n':
                self.accessing_to_database("UPDATE training_data SET train_correct='0', train_incorrect='1', train_give_answ='1' WHERE train_id={}".format(answ_id), True)
            else:
                self.accessing_to_database("UPDATE training_data SET train_give_answ='1' WHERE train_id={}".format(answ_id), True)
        else:
            self.msg = self.bad_answer

        self.save_to_chat(self.channel, self.uch)
        self.push_socket(self.channel, self.uch, self.msg)

    def handle_answer(self, question):
        if self.subj_id != 0:
            self.push_socket(self.channel, self.uch, "I think you will find this information in")
            if self.act_id == 0:
                self.msg = "http://help.floctopus.com/articles/?cat={}".format(self.subj_id)
            else:
                self.msg = "http://help.floctopus.com/articles/view/{}".format(self.act_id)
        else:
            self.msg = self.bad_answer

        self.save_to_chat(self.channel, self.uch)
        self.push_socket(self.channel, self.uch, self.msg)

        if self.msg != self.bad_answer:
            columns = self.accessing_to_database("SELECT * FROM users WHERE user_pusher_channel='{}'".format(self.uch))
            user_id = columns[0]
            self.save_to_train_data(question, self.msg, user_id)
            self.msg = "Tell me, please, this information was useful for you? Yes or No?"

            self.save_to_chat(self.channel, self.uch)
            self.push_socket(self.channel, self.uch, self.msg)

        self.db.close()

    def find_similar_question(self, question):
        columns = self.accessing_to_database("SELECT * FROM training_data WHERE train_question='{}' LIMIT 1".format(self.msg))
        if not columns:
            return False
        else:
            self.push_socket(self.channel, self.uch, "I think you will find this information in")
            self.msg = columns[2]
            self.save_to_chat(self.channel, self.uch)
            self.push_socket(self.channel, self.uch, self.msg)
            columns = self.accessing_to_database("SELECT * FROM users WHERE user_pusher_channel='{}'".format(self.uch))
            user_id = columns[0]
            self.save_to_train_data(question, self.msg, user_id)

            self.msg = "Tell me, please, this information was useful for you? Yes or No?"

            self.save_to_chat(self.channel, self.uch)
            self.push_socket(self.channel, self.uch, self.msg)

            self.db.close()
            return True
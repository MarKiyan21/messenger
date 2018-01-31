import json
import MySQLdb
from channels import Group
from channels.sessions import channel_session
from .bot import send_bot
from .models import Chats
# from channels.auth import channel_session_user_from_http

@channel_session
# @channel_session_user_from_http
def connect(message):
    message.reply_channel.send({
        "accept": True
    })
    ch = message.content["path"][1:]
    message.channel_session["ch"] = ch
    db = MySQLdb.connect(host='localhost', user='root', passwd='root', db='bd')
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_pusher_channel='{}'".format(ch))
    columns = cursor.fetchone()
    cursor.close()
    db.close()
    if columns:
        Group(ch).add(message.reply_channel)
    else:
        message.reply_channel.send({
            "close": True
        })
    # uch = message.content['path'][1:]
    # Group("chat").add(message.reply_channel)

# @channel_session
def receive(message):
    data = json.loads(message["text"])
    msg = data["msg"]
    channel = data["channel"]
    uch = data["uch"]
    if channel == "floctoid":
        send_bot(msg, uch)
    else:
        Group(channel).send({
            "text": msg,
        })
        chat = Chats(chat_from=uch, chat_to=channel, chat_msg=msg)
        chat.save()
    Group(uch).send({
        'text': msg
    })
    # Group("chat").send({
    #     'text': message.content['text']
    # })

@channel_session
def disconnect(message):
    Group(message.channel_session["ch"]).discard(message.reply_channel)
    # Group("chat").discard(message.reply_channel)
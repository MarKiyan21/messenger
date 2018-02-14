import json
import MySQLdb
from channels import Group
from channels.sessions import channel_session
from .bot import send_bot
from .models import Chats, Websockets
from project.settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD,MYSQL_NAME
# from channels.auth import channel_session_user_from_http

@channel_session
# @channel_session_user_from_http
def connect(message):
    message.reply_channel.send({
        "accept": True
    })
    groups_ch = []
    ch = message.content["path"][1:]
    message.channel_session["ch"] = ch
    # print(ch)
    db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWD, db=MYSQL_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE user_pusher_channel='{}'".format(ch))
    columns = cursor.fetchone()
    if columns:
        Group(ch).add(message.reply_channel)
        cursor.execute("SELECT * FROM websockets WHERE ws_user_id='{}'".format(columns[0]))
        col = cursor.fetchone()
        if col:
            cursor.execute("UPDATE websockets SET ws_reply_channel='{}' WHERE ws_user_id={}".format(message.reply_channel, col[1]))
            db.commit()
            message.channel_session["user_id"] = col[1]
        else:
            ws_sock = Websockets(ws_user_id=columns[0], ws_reply_channel=message.reply_channel)
            ws_sock.save()
            message.channel_session["user_id"] = columns[0]
        cursor.execute("SELECT gr_mem_id_group FROM group_members WHERE gr_mem_id_user='{}'".format(message.channel_session["user_id"]))
        for tpl in cursor:
            groups_ch.append(tpl[0])
        for gr_ch in groups_ch:
            cursor.execute("SELECT groups_channel FROM groups WHERE groups_id='{}'".format(gr_ch))
            for tpl in cursor:
                Group(tpl[0]).add(message.reply_channel)
                print ("ЮЗЕР ПРИКОНЕКТИЛСЯ К ГРУППЕ {}, КАНАЛ КОТОРОГО - {}".format(tpl[0], message.reply_channel))
    else:
        message.reply_channel.send({
            "close": True
        })
    cursor.close()
    db.close()
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
        chat = Chats(chat_from=uch, chat_to=channel, chat_msg=msg)
        chat.save()
        last_id = Chats.objects.latest('chat_id').chat_id
        ret = json.dumps({"id": last_id, "from": uch, "msg": msg, "status": 0})
        Group(channel).send({
            "text": ret
        })
    # Group(uch).send({
    #     "text": msg
    # })
    # Group("chat").send({
    #     'text': message.content['text']
    # })

@channel_session
def disconnect(message):
    # шукати в яких групах є і з усіх робити disconnect
    groups_ch = []
    db = MySQLdb.connect(host=MYSQL_HOST, user=MYSQL_USER, passwd=MYSQL_PASSWD, db=MYSQL_NAME)
    cursor = db.cursor()
    cursor.execute("SELECT gr_mem_id_group FROM group_members WHERE gr_mem_id_user='{}'".format(message.channel_session["user_id"]))
    for tpl in cursor:
        groups_ch.append(tpl[0])
    for gr_ch in groups_ch:
        cursor.execute("SELECT groups_channel FROM groups WHERE groups_id='{}'".format(gr_ch))
        for tpl in cursor:
            Group(tpl[0]).discard(message.reply_channel)
            print ("ЮЗЕР ОТКОНЕКТИЛСЯ ОТ ГРУППЫ {}, КАНАЛ КОТОРОГО - {}".format(tpl[0], message.reply_channel))
    cursor.close()
    db.close()
    Group(message.channel_session["ch"]).discard(message.reply_channel)
    # Group("chat").discard(message.reply_channel)
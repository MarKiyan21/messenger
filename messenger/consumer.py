import json
import ast
from channels import Group
from channels.sessions import channel_session
from urllib.parse import parse_qs as qs

@channel_session
def priv_connect(message):
    message.reply_channel.send({
        "accept": True
    })
    # params = qs(message.content["query_string"])
    print(channel_session)
    # d = message.content["text"]
    # d = ast.literal_eval(message.content["text"])
    # print(message.content)
    Group("private").add(message.reply_channel)

@channel_session
def priv_receive(message):
    # print(message.content["text"])
    Group("private").send({
        # "text": json.dumps({
        "text": message.content["text"],
        # })
    })
    # message.reply_channel.send({
    #     "text": message.content['text'],
    # })

def priv_disconnect(message):
    # print(message.content)
    Group("private").discard(message.reply_channel)
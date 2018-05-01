import requests
from .brains import Brains
from .handling import Handle
from project.settings import SECRET
from channels import Group

def send_bot(msg, gr_id, gr_channel, user_id, uch):
    brain = Brains()
    handle = Handle(gr_channel, gr_id, user_id, uch, msg)
    handle.save_to_chat(handle.user_id, handle.gr_id)
    handle.msg = handle.msg.lower()
    msg = handle.msg.strip()

    if msg == "hello!" or msg == "hi!" or msg == "hello" or msg == "hi":
        handle.handle_greeting()
        return

    if msg == 'yes' or msg == 'no' or msg == 'y' or msg == 'n':
        handle.handle_confirmation(msg)
        return

    if handle.find_similar_question(msg):
        return
    else:
        semantic_core = brain.find_semantic_core(msg)
        if semantic_core:
            # subject = handle.db.cursor()
            # subject.execute("SELECT * FROM help_docs_category")
            url = 'https://api.floctopus.com/v1/messenger/chat/gethdallcat'
            params = {}
            headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
            resp = requests.get(url, params=params, headers=headers)
            data = resp.json()
            if data['status'] == 1:

            # numrows = len(data['cat']) - 1
                i = 0
                ret = ""
                for elem in semantic_core:
                    for key,value in elem.items():
                        if key == 'none':
                            handle.msg = "What do you want " + str(value) + "?"
                            handle.save_to_chat("-1", handle.gr_id)
                            handle.push_socket(handle.msg)
                            return
                        while i < len(data['cat']):
                            some = data['cat'][i]['hdoccat_tags'].split(" ")
                            for word in some:
                                if key == word:
                                    handle.subj_id = data['cat'][i]['hdoccat_id']
                                    break
                            if handle.subj_id != 0:
                                break
                            i += 1

                i = 0
                if handle.subj_id != 0:
                    url = 'https://api.floctopus.com/v1/messenger/chat/gethdbycatid'
                    params = {'catid': handle.subj_id}
                    headers = {'Content-Type':'application/json', 'Access-Key':SECRET}
                    resp = requests.get(url, params=params, headers=headers)
                    data = resp.json()
                    if data['status'] == 1:
                    # action = handle.db.cursor()
                    # action.execute("SELECT * FROM help_docs WHERE hdoc_cat=" + str(handle.subj_id))
                    # numrows = action.rowcount
                        for elem in semantic_core:
                            for key,value in elem.items():
                                while i < len(data['hd']):
                                    some = data['hd'][i]['hdoc_tags'].split(" ")
                                    if some[0] != "":
                                        for word in some:
                                            if value == word:
                                                handle.act_id = data['hd'][i]['hdoc_id']
                                                break
                                if handle.act_id != 0:
                                    break
        handle.handle_answer(msg)
    return


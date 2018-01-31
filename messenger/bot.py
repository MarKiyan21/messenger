from .brains import Brains
from .handling import Handle
from .models import Chats
from channels import Group

def send_bot(msg, uch):
    brain = Brains()
    handle = Handle("floctoid", msg.lower(), uch)
    msg = handle.msg.strip()
    handle.save_to_chat(handle.uch, handle.channel)

    if msg == "hello!" or msg == "hi!" or msg == "hello" or msg == "hi":
        handle.handle_greeting()
        return

    if msg == 'yes' or msg == 'no' or msg == 'y' or msg == 'n':
        Group(uch).send({
            "text": "Wait please, I put your answer in our database :)",
        })
        handle.handle_confirmation(msg)
        return

    if handle.find_similar_question(msg):
        return
    else:
        semantic_core = brain.find_semantic_core(msg)
        if semantic_core:
            subject = handle.db.cursor()
            subject.execute("SELECT * FROM help_docs_category")
            numrows = subject.rowcount
            ret = ""
            for elem in semantic_core:
                for key,value in elem.items():
                    if key == 'none':
                        handle.msg = "What do you want " + str(value) + "?"

                        handle.save_to_chat(handle.channel, handle.uch)
                        handle.push_socket(handle.uch, handle.msg)
                        return
                    for x in range(0, numrows):
                        column = subject.fetchone()
                        some = column[4].split(" ")
                        for word in some:
                            if key == word:
                                handle.subj_id = x + 1
                                break
                        if handle.subj_id != 0:
                            break

            if handle.subj_id != 0:
                action = handle.db.cursor()
                action.execute("SELECT * FROM help_docs WHERE hdoc_cat=" + str(handle.subj_id))
                numrows = action.rowcount
                for elem in semantic_core:
                    for key,value in elem.items():
                        for x in range(0, numrows):
                            column = action.fetchone()
                            some = column[5].split(" ")
                            if some[0] != "":
                                for word in some:
                                    if value == word:
                                        handle.act_id = x + 1
                                        break
                        if handle.act_id != 0:
                            break
        handle.handle_answer(msg)
    return
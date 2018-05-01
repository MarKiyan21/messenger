import os
import sys
import six
import argparse
import textwrap

import googleapiclient.discovery
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types

from django.shortcuts import HttpResponse

class Brains(object):

    def __init__(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/opt/messenger/messenger/key/Floctopus-6c3d81f7772b.json"

    def dependents(self, tokens, head_index):
        head_to_deps = {}
        for i, token in enumerate(tokens):
            head = token['dependencyEdge']['headTokenIndex']
            if i != head:
                head_to_deps.setdefault(head, []).append(i)
        return head_to_deps.get(head_index, ())

    def phrase_text_for_head(self, tokens, text, head_index):
        begin = tokens[head_index]['text']['beginOffset']
        end = begin + len(tokens[head_index]['text']['content'])
        return text[begin:end]

    def analyze_syntax(self, text):
        service = googleapiclient.discovery.build('language', 'v1beta1')
        body = {
            'document': {
                'type': 'PLAIN_TEXT',
                'content': text,
            },
            'features': {
                'extract_syntax': True,
            },
            'encodingType': self.get_native_encoding_type(),
        }
        request = service.documents().annotateText(body=body)
        return request.execute()
    def get_native_encoding_type(self):
        if sys.maxunicode == 65535:
            return 'UTF16'
        else:
            return 'UTF32'

    def entities_text(self, text):
        client = language.LanguageServiceClient()

        if isinstance(text, six.binary_type):
            text = text.decode('utf-8')

        document = types.Document(
            content=text,
            type=enums.Document.Type.PLAIN_TEXT)

        entities = client.analyze_entities(document).entities

        ret = []
        dictWithEntity = {}

        for entity in entities:
            ret.append({entity.name: ""})

        return ret

    def find_triples(self, tokens,
                 head_part_of_speech='VERB',
                 right_dependency_label='DOBJ'):
        for head, token in enumerate(tokens):
            if token['partOfSpeech']['tag'] == head_part_of_speech:
                children = self.dependents(tokens, head)
                right_deps = []
                for child in children:
                    child_token = tokens[child]
                    child_dep_label = child_token['dependencyEdge']['label']
                    if child_dep_label == right_dependency_label:
                        right_deps.append(child)
                for right_dep in right_deps:
                    yield (head, right_dep)

    def show_triple(self, tokens, text, triple):
        verb, dobj = triple

        verb_text = tokens[verb]['text']['content']
        dobj_text = self.phrase_text_for_head(tokens, text, dobj)

        dictWithVerbAndDobj = {}
        dictWithVerbAndDobj[dobj_text] = verb_text
        return dictWithVerbAndDobj

    def find_semantic_core(self, text):
        count = 0
        retList = []

        analysis = self.analyze_syntax(text)
        tokens = analysis.get('tokens', [])

        #retList = []

        for triple in self.find_triples(tokens):
            retList.append(self.show_triple(tokens, text, triple))
            count += 1

        if count == 0:
            retList = self.entities_text(text)
            #retList.append(self.entities_text(text))
            #return(retDict)

        #CHANGE AFTER NEED MORE ANSWERS THAN ONE!!!
        if not retList:
            ret = [{"":""}]
        else:
            ret = [retList[0]]
        ###

        for oldkey,value in ret[0].items():
            if oldkey == 'it' or oldkey == 'them':
                client = language.LanguageServiceClient()
                document = types.Document(
                    content=text,
                    type=enums.Document.Type.PLAIN_TEXT)
                entities = client.analyze_entities(document).entities
                if entities:
                    for entity in entities:
                        newkey = entity.name
                        break
                else:
                    newkey = "none"
                ret[0][newkey] = ret[0].pop(oldkey)
        return(ret)



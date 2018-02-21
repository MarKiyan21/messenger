from django.conf.urls import url
from .views import chat, getUsers, getGroups, getMessages, createGroup, translateMessage

urlpatterns = [
    url(r'^chat/$', chat, name='chat'),
    url(r'^getUsers/$', getUsers, name='getUsers'),
    url(r'^getGroups/$', getGroups, name='getGroups'),
    url(r'^getMessages/$', getMessages, name='getMessages'),
    url(r'^createGroup/$', createGroup, name='createGroup'),
    url(r'^translateMessage/$', translateMessage, name='translateMessage'),
]
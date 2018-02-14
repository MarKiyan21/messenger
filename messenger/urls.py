from django.conf.urls import url
from .views import chat, getUsers, getGroups, createGroup

urlpatterns = [
    url(r'^chat/$', chat, name='chat'),
    url(r'^getUsers/$', getUsers, name='getUsers'),
    url(r'^getGroups/$', getGroups, name='getGroups'),
    url(r'createGroup$', createGroup, name='createGroup'),
]
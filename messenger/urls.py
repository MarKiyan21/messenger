from django.conf.urls import url
from .views import chat, getUsers

urlpatterns = [
    url(r'^chat/$', chat, name='chat'),
    url(r'^getUsers/$', getUsers, name='getUsers'),
]
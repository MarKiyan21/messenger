from django.conf.urls import url
from .views import createGroup, getGroups, translateMessage

urlpatterns = [
    url(r'^createGroup/$', createGroup, name='createGroup'),
    url(r'^getGroups/$', getGroups, name='getGroups'),
    url(r'^translateMessage/$', translateMessage, name='translateMessage'),
]

from django.db import models
from channels import Group

from django.utils.six import python_2_unicode_compatible

@python_2_unicode_compatible
class Room(models.Model):
    title = models.CharField(max_length=255)
    staff_only = models.BooleanField(default=False)

    def str(self):
        return self.title

    @property
    def websocket_group(self):
        return Group("room-{}".format(self.id))
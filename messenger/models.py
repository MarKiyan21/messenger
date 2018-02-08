from django.db import models

class Chats(models.Model):
    chat_id = models.AutoField(primary_key=True)
    chat_from = models.CharField(max_length=200, blank=True, null=True)
    chat_to = models.CharField(max_length=200, blank=True, null=True)
    chat_msg = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chats'

class Groups(models.Model):
    groups_id = models.AutoField(primary_key=True)
    groups_name = models.CharField(max_length=255, blank=True, null=True)
    groups_channel = models.CharField(max_length=255, blank=True, null=True)
    groups_members = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'groups'

class TrainingData(models.Model):
    train_id = models.AutoField(primary_key=True)
    train_question = models.TextField(blank=True, null=True)
    train_answer = models.CharField(max_length=250, blank=True, null=True)
    train_user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'training_data'
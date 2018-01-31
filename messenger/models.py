from django.db import models

# class GroupChat(models.Model):
#     gr_chat_id = models.AutoField(primary_key=True)
#     gr_chat_from = models.CharField(max_length=255, blank=True, null=True)
#     gr_chat_to = models.CharField(max_length=255, blank=True, null=True)
#     gr_chat_msg = models.CharField(max_length=255, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'group_chat'

class Chats(models.Model):
    chat_id = models.AutoField(primary_key=True)
    chat_from = models.CharField(max_length=200, blank=True, null=True)
    chat_to = models.CharField(max_length=200, blank=True, null=True)
    chat_msg = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chats'

# class Users(models.Model):
#     users_id = models.AutoField(primary_key=True)
#     users_username = models.CharField(max_length=255, blank=True, null=True)
#     users_channel = models.IntegerField(blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'users'

class TrainingData(models.Model):
    train_id = models.AutoField(primary_key=True)
    train_question = models.TextField(blank=True, null=True)
    train_answer = models.CharField(max_length=250, blank=True, null=True)
    train_user_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'training_data'
# chatbot/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # カスタムフィールドを追加
    birthday = models.DateField(null=True, blank=True)

    # groupsとuser_permissionsにrelated_nameを追加
    groups = models.ManyToManyField('auth.Group', related_name='chatbot_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='chatbot_user_permissions_set', blank=True)

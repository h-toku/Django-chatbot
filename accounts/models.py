# accounts/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager

class CustomUser(AbstractUser):
    # カスタムフィールドを追加
    objects = UserManager()  # birthdayはそのまま残す

    # groupsとuser_permissionsにrelated_nameを追加
    groups = models.ManyToManyField('auth.Group', related_name='accounts_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='accounts_user_permissions_set', blank=True)

# chatbot/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # カスタムフィールドを追加
    birthday = models.DateField(null=True, blank=True)

    # groupsとuser_permissionsにrelated_nameを追加
    groups = models.ManyToManyField('auth.Group', related_name='chatbot_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='chatbot_user_permissions_set', blank=True)
class Message(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)  # ←追加
    session_id = models.CharField(max_length=100)
    role = models.CharField(max_length=10)  # 'user' or 'ai'
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.text[:30]}"
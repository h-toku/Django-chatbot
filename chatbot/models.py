# chatbot/models.py
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.utils import timezone

class CustomUser(AbstractUser):
    # メールアドレスをユーザー名として使用
    username = None
    email = models.EmailField('メールアドレス', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # カスタムフィールドを追加
    birthday = models.DateField(null=True, blank=True)

    # groupsとuser_permissionsにrelated_nameを追加
    groups = models.ManyToManyField('auth.Group', related_name='chatbot_user_set', blank=True)
    user_permissions = models.ManyToManyField('auth.Permission', related_name='chatbot_user_permissions_set', blank=True)

    def __str__(self):
        return self.email

class ChatMessage(models.Model):
    """
    チャットメッセージを保存するモデル
    """
    session_id = models.CharField(max_length=255, db_index=True)
    role = models.CharField(max_length=10)  # 'user' または 'ai'
    message = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session_id', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.role}: {self.message[:50]}"

User = get_user_model()

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conversations')
    prompt = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

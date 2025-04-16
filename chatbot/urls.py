from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', home, name='home'),  # チャット画面の表示
    path('api/chat/', views.chat, name='chat_api'),  # APIエンドポイント
    path('chat/', views.chat, name='chat'),
]

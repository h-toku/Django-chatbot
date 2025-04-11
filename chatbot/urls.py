from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.chat_page, name='chat_page'),  # チャット画面の表示
    path('api/chat/', views.chat, name='chat_api'),  # APIエンドポイント
    path('chat/', views.chat, name='chat'),
]

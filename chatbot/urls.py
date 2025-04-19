from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from chatbot.views import home

urlpatterns = [
    path('api/chat/', views.chat, name='chat_api'),  # APIエンドポイント
    path('', views.chat, name='chat'),
    path('chat/', views.chat, name='chat'),
    path('chat/history/', views.chat_history, name='chat_history'),
    path('conversation/save/', views.save_conversation, name='save_conversation'),
    path('conversation/history/', views.get_conversation_history, name='conversation_history'),
    ]

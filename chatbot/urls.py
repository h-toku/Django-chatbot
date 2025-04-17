from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from chatbot.views import home

urlpatterns = [
    path('api/chat/', views.chat, name='chat_api'),  # APIエンドポイント
    path('', views.chat, name='chat'),
    path('save/', views.save_conversation, name='save_conversation'),
    path('history/', views.get_conversation_history, name='get_conversation_history'),
]

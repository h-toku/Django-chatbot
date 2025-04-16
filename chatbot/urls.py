from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from chatbot.views import home

urlpatterns = [
    path('', home, name='home'), 
    path('api/chat/', views.chat, name='chat_api'),  # APIエンドポイント
    path('chat/', views.chat, name='chat'),
]

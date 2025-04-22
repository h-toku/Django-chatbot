from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chat_view, name='chat'),
    path('api/', views.chat_api, name='chat_api'),
    path('history/', views.chat_history, name='chat_history'),
    path('conversation/save/', views.save_conversation, name='save_conversation'),
    path('conversation/history/', views.get_conversation_history, name='conversation_history'),
]

from django.urls import path
from .views import chat, chat_page  # ✅ chat_page を追加

urlpatterns = [
    path("api/chat/", chat, name="chat_api"),  # API
    path("chat/", chat_page, name="chat_page"),  # HTMLページ
]


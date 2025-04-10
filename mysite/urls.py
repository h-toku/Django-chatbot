from django.contrib import admin
from django.urls import path, include
from chatbot import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chatbot.urls')),
]
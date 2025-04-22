from django.contrib import admin
from django.urls import path, include
from chatbot.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chat/', include('chatbot.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', home, name='home'),
]

from django.urls import path
from . import views
from .views import CustomLoginView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLoginView.as_view(), name='logout'),
]
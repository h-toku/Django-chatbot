from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLoginView.as_view(), name='logout'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('account/delete/', views.account_delete, name='account_delete'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
]
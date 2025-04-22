from django.urls import path
from . import views
from .views import CustomLoginView
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetView

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('verification-sent/', views.verification_sent, name='verification_sent'),
    path('resend-verification/', views.resend_verification_email, name='resend_verification'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('account/delete/', views.account_delete, name='account_delete'),
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
]

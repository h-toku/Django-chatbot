# accounts/forms.py

from django import forms
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        email = cleaned_data.get("email")

        # メールアドレスの重複チェック
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("このメールアドレスは既に登録されています。")

        # パスワードが一致しない場合
        if password and confirm_password and password != confirm_password:
            raise ValidationError("パスワードが一致しません。")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # パスワードのハッシュ化
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("メールアドレスかパスワードが間違っています"),
                code='inactive',
            )
# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
import traceback
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy, reverse
from django.conf import settings
import logging
from django.utils import timezone
from datetime import timedelta
from django.utils.html import strip_tags
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import AuthenticationForm
from django import forms

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def form_invalid(self, form):
        email = form.cleaned_data.get('username')
        if email:
            try:
                user = get_user_model().objects.get(email=email)
                if not user.is_active:
                    # 認証メールを再送
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    domain = get_current_site(self.request).domain
                    activation_link = f"http://{domain}/activate/{uid}/{token}/"

                    subject = "【AIチャットボット】メール認証のお願い"
                    from_email = settings.DEFAULT_FROM_EMAIL
                    to_email = user.email
                    text_content = "このメールはHTML表示に対応していない環境では読み取れません。"
                    html_content = render_to_string("accounts/activate_email.html", {
                        'user': user,
                        'activation_link': activation_link,
                        'site_name': 'AIチャットボット',
                    })

                    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    messages.info(self.request, 'アカウントが有効化されていません。認証メールを再送しました。')
                    return redirect('accounts:login')
            except get_user_model().DoesNotExist:
                pass

        messages.error(self.request, 'メールアドレスかパスワードが間違っています。')
        return super().form_invalid(form)


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "パスワードが正常にリセットされました。")
        return redirect('chatbot:chat')


class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset_form.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = get_user_model().objects.get(email=email)
            if not user.is_active:
                logger.warning(f"無効なアカウント: {email}")
                messages.error(self.request, 'このアカウントは有効化されていません。')
                return redirect('accounts:login')

            logger.info(f"パスワードリセットメール送信開始: {email}")
            response = super().form_valid(form)
            logger.info(f"パスワードリセットメール送信成功: {email}")
            messages.success(self.request, 'パスワードリセットのメールを送信しました。')
            return response
        except get_user_model().DoesNotExist:
            logger.warning(f"存在しないメールアドレス: {email}")
            messages.error(self.request, 'このメールアドレスは登録されていません。')
            return redirect('accounts:login')
        except Exception as e:
            logger.error(f"パスワードリセットメール送信エラー: {str(e)}")
            messages.error(self.request, 'メール送信中にエラーが発生しました。')
            return redirect('accounts:login')


class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label='メールアドレス',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='パスワード',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not user.is_active:
                messages.error(request, 'このアカウントは有効化されていません。')
                return redirect('accounts:login')
            login(request, user)
            return redirect('chatbot:chat')
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'ログアウトしました。')
    return redirect('accounts:login')


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        logger.info("📨 フォーム送信あり")
        email = request.POST.get('email')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            logger.info(f"メールアドレスが既に登録されています: {email}")
            messages.error(request, 'このメールアドレスは既に登録されています。')
            return redirect('accounts:register')

        if form.is_valid():
            logger.info("✅ フォームバリデーションOK")
            user = form.save(commit=False)
            user.username = email
            user.email = email
            user.is_active = False
            user.save()

            try:
                logger.info("📧 メール送信処理に入る")
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                activation_url = request.build_absolute_uri(
                    reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})
                )

                context = {
                    'user': user,
                    'activation_url': activation_url,
                    'site_name': 'AIチャットボット'
                }

                html_message = render_to_string('accounts/email/activation_email.html', context)
                plain_message = strip_tags(html_message)

                send_mail(
                    '【AIチャットボット】メール認証のお願い',
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=False,
                )

                logger.info(f"📧 メール送信成功: {user.email}")
                messages.success(request, "認証メールを送信しました。メールに記載されたリンクからアカウントを有効化してください。")
            except Exception as e:
                logger.error(f"メール送信失敗: {str(e)}")
                traceback.print_exc()
                messages.error(request, "メール送信中にエラーが発生しました。")

            return redirect('accounts:verification_sent')
        else:
            logger.info(f"❌ フォームエラー: {form.errors}")
            messages.error(request, '登録に失敗しました。もう一度お試しください。')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, 'このアカウントは既に有効化されています。')
            return redirect('accounts:login')

        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'メール認証が完了しました。ログインされました。')
        return redirect('chatbot:chat')
    else:
        messages.error(request, 'リンクが無効です。')
        return redirect('accounts:login')


def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                messages.error(request, 'このアカウントは有効化されていません。')
                return redirect('accounts:login')

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_url = request.build_absolute_uri(
                reverse('accounts:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
            )

            context = {
                'user': user,
                'reset_url': reset_url,
                'site_name': 'AIチャットボット'
            }

            html_message = render_to_string('accounts/email/password_reset_email.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                '【AIチャットボット】パスワードリセット',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, "パスワードリセットのメールを送信しました。")
            return redirect('accounts:password_reset_done')

        except User.DoesNotExist:
            messages.error(request, 'このメールアドレスは登録されていません。')
            return redirect('accounts:password_reset')

    return render(request, 'accounts/password_reset_form.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        try:
            User = get_user_model()
            user = User.objects.get(email=email)

            if user.check_password(password):
                if not user.is_active:
                    # 認証メールを再送
                    token = default_token_generator.make_token(user)
                    uid = urlsafe_base64_encode(force_bytes(user.pk))
                    activation_url = request.build_absolute_uri(
                        reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})
                    )

                    context = {
                        'user': user,
                        'activation_url': activation_url
                    }

                    html_message = render_to_string('accounts/email/activation_email.html', context)
                    plain_message = strip_tags(html_message)

                    send_mail(
                        'アカウントの認証（再送）',
                        plain_message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        html_message=html_message,
                        fail_silently=False,
                    )

                    messages.info(request, 'アカウントが有効化されていません。認証メールを再送しました。')
                    return redirect('accounts:verification_sent')

                login(request, user)
                messages.success(request, 'ログインしました。')
                return redirect('chatbot:chat')
            else:
                messages.error(request, 'パスワードが正しくありません。')
        except User.DoesNotExist:
            messages.error(request, 'このメールアドレスは登録されていません。')

    form = CustomAuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def account_delete(request):
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "アカウントが正常に削除されました。")
        return redirect('accounts:login')

    return render(request, 'accounts/account_delete.html')


def verification_sent(request):
    return render(request, 'accounts/verification_sent.html')


def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = get_user_model().objects.get(email=email, is_active=False)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            activation_url = request.build_absolute_uri(
                reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})
            )

            context = {
                'user': user,
                'activation_url': activation_url
            }

            html_message = render_to_string('accounts/email/activation_email.html', context)
            plain_message = strip_tags(html_message)

            send_mail(
                'アカウントの認証（再送）',
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, '認証メールを再送しました。メールをご確認ください。')
        except get_user_model().DoesNotExist:
            messages.error(request, '指定されたメールアドレスの未認証アカウントが見つかりません。')
    return redirect('accounts:verification_sent')


def password_reset_done(request):
    return render(request, 'accounts/password_reset_done.html')


def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, 'パスワードが正常にリセットされました。')
                return redirect('accounts:login')
        else:
            form = SetPasswordForm(user)
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
    else:
        messages.error(request, 'パスワードリセットのリンクが無効です。')
        return redirect('accounts:login')


def password_reset_complete(request):
    return render(request, 'accounts/password_reset_complete.html')


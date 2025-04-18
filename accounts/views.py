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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
import traceback
from django.contrib.auth.views import PasswordResetCompleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'メールアドレスかパスワードが間違っています。')
        return super().form_invalid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    def form_valid(self, form):
        # パスワードリセット後に自動的にログインする処理
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "パスワードが正常にリセットされました。")
        return redirect('chat_page')  # チャットページにリダイレクト
    
class CustomPasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset_form.html'
    success_url = reverse_lazy('password_reset_done')  # 成功時に遷移するURL
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'  # メール本文テンプレート

    def form_valid(self, form):
        print("📨 パスワードリセットフォームがバリデーションOK")
        response = super().form_valid(form)
        return response

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('chat_page')  # 適宜変更
        else:
            messages.error(request, 'ユーザー名またはパスワードが間違っています')

    return render(request, 'registration/login.html')

def user_logout(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        logger.info("📨 フォーム送信あり")
        email = request.POST.get('email')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            logger.info("メールアドレスが既に登録されています:", email)
            messages.error(request, 'このメールアドレスは既に登録されています。')
            return redirect('register')
            
        
        if form.is_valid():
            logger.info("✅ フォームバリデーションOK")
            user = form.save(commit=False)
            user.is_active = False  # 初期状態で非アクティブ
            user.save()

            try:
                logger.info("📧 メール送信処理に入る")
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                domain = get_current_site(request).domain
                activation_link = f"http://{domain}/activate/{uid}/{token}/"
            
                subject = "【AIチャットボット】メール認証のお願い"
                from_email = settings.DEFAULT_FROM_EMAIL
                to_email = user.email
                text_content = "このメールはHTML表示に対応していない環境では読み取れません。"
                html_content = render_to_string("registration/activate_email.html", {
                    'user': user,
                    'activation_link': activation_link,
                })
            
                msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
                msg.attach_alternative(html_content, "text/html")
                msg.send()
            
                messages.success(request, "認証メールを送信しました。")
            except Exception as e:
                logger.error(f"メール送信失敗: {str(e)}")
                traceback.print_exc()
                messages.error(request, "メール送信中にエラーが発生しました。")
                
            return redirect('register')
        else:
            logger.info("❌ フォームエラー:", form.errors)
            messages.error(request, '登録に失敗しました。もう一度お試しください。')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'メール認証が完了しました。ログインされました。')
        return redirect('chat_page')
    else:
        messages.error(request, 'リンクが無効です。')
        return redirect('login')
    
def password_reset(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain
            activation_link = f"http://{domain}/reset/{uid}/{token}/"

            subject = "【AIチャットボット】パスワードリセットのお願い"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = user.email
            text_content = "このメールはHTML表示に対応していない環境では読み取れません。"
            html_content = render_to_string("registration/password_reset_email.html", {
                'user': user,
                'activation_link': activation_link,
            })

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            messages.success(request, "パスワードリセットメールを送信しました。")
            return redirect('login')  # パスワードリセット後はログインページにリダイレクト

        except User.DoesNotExist:
            messages.error(request, 'このメールアドレスは登録されていません。')
        except Exception as e:
            messages.error(request, f"予期しないエラーが発生しました: {str(e)}")

    return render(request, 'registration/password_reset_form.html')
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=email, password=password)  # ユーザー名をemailに変更
        if user is not None:
            login(request, user)
            return redirect('chat_page')
        else:
            messages.error(request, 'メールアドレスまたはパスワードが正しくありません')

    return render(request, 'registration/login.html')

@login_required
def account_delete(request):
    if request.method == "POST":
        user = request.user
        user.delete()  # ユーザーの削除
        messages.success(request, "アカウントが正常に削除されました。")
        return redirect('login')  # ログインページにリダイレクト

    return render(request, 'account_delete.html')


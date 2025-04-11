# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import RegisterForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        messages.error(self.request, 'メールアドレスかパスワードが間違っています。')
        return super().form_invalid(form)

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
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # 初期状態で非アクティブ
            user.save()

            # メールを送信
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode()).decode()
            domain = get_current_site(request).domain
            activation_link = f"{get_current_site(request).domain}/activate/{uid}/{token}/"
            # メール送信のロジック
                        # ✅ メール送信
            subject = "【AIチャットボット】メール認証のお願い"
            from_email = "noreply@example.com"
            to_email = user.email
            text_content = "このメールはHTML表示に対応していない環境では読み取れません。"
            html_content = render_to_string("emails/activation_email.html", {
                'user': user,
                'activation_link': activation_link,
            })

            # ✅ HTMLメールを送信
            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            messages.success(request, "認証メールを送信しました。")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'メール認証が完了しました。ログインされました。')
        return redirect('chat_page')  # 適切なページへ
    else:
        messages.error(request, 'リンクが無効です。')
        return redirect('login')
    
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat_page')
            else:
                messages.error(request, 'メールアドレスまたはパスワードが正しくありません')
        except User.DoesNotExist:
            messages.error(request, 'ユーザーが存在しません')

    return render(request, 'registration/login.html')
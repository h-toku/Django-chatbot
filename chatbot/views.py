from django.shortcuts import render, redirect
from django.http import JsonResponse
import re
from .models import Message
from django.contrib.auth.decorators import login_required
from .utils import query_huggingface

def home(request):
    return render(request, 'chatbot/home.html')

def chatbot_view(request):
    if request.method == 'POST':
        user_input = request.POST.get('message', '')
        prompt = f"ユーザー: {user_input}\nAI:"
        try:
            reply = query_huggingface(prompt)
        except Exception as e:
            reply = f"エラーが発生しました: {str(e)}"
        return JsonResponse({'response': reply})

def chat_page(request):
    return render(request, 'chatbot/chat.html')

def get_prompt_from_history(session_id, latest_user_input, max_messages=10):
    messages = Message.objects.filter(session_id=session_id).order_by('-timestamp')[:max_messages][::-1]
    lines = []

    for m in messages:
        if m.role == 'user':
            lines.append(f"ユーザー: {m.text}")
        else:
            lines.append(f"AI: {m.text}")

    lines.append(f"ユーザー: {latest_user_input}")
    lines.append("AI:")

    return "\n".join(lines)

def chat(request):
    session_id = request.session.session_key or request.session.create()

    if request.method == 'GET':
        # 非ログイン時は履歴表示しない
        if request.user.is_authenticated:
            messages = Message.objects.filter(session_id=session_id).order_by('timestamp')
        else:
            messages = []  # 履歴を表示しない
        return render(request, 'chat.html', {'messages': messages})

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if user_input:
            try:
                # 履歴からプロンプト作成
                messages = Message.objects.filter(session_id=session_id).order_by('-timestamp')[:10][::-1]
                lines = []
                for m in messages:
                    role = "ユーザー" if m.role == "user" else "AI"
                    lines.append(f"{role}: {m.text}")
                lines.append(f"ユーザー: {user_input}")
                lines.append("AI:")

                prompt = "\n".join(lines)
                print(prompt)

                response = query_huggingface(prompt)

                response = re.sub(r"http\S+|pic\.twitter\.com/\S+|<unk>", "", response).strip()

                # ログイン時のみ履歴保存
                if request.user.is_authenticated:
                    Message.objects.create(session_id=session_id, role='user', text=user_input)
                    Message.objects.create(session_id=session_id, role='ai', text=response)

                return JsonResponse({"response": response})
            except Exception as e:
                return JsonResponse({"response": f"AIエラー: {str(e)}"})
        else:
            return JsonResponse({"response": "入力が空です。"})

    else:
        # GET時に履歴を取得してテンプレートへ渡す
        if request.user.is_authenticated:
            messages = Message.objects.filter(session_id=session_id).order_by('timestamp')
        else:
            messages = []  # 非ログイン時は履歴を表示しない
        return render(request, 'chat.html', {'messages': messages})

def save_message(request, session_id, role, text):
    # ログインしている場合のみ履歴を保存
    if request.user.is_authenticated:
        Message.objects.create(session_id=session_id, role=role, text=text)

def chat_history(request):
    session_id = request.session.session_key
    if not session_id:
        return JsonResponse({"history": []})

    messages = Message.objects.filter(session_id=session_id).order_by('timestamp')
    history = [{"role": m.role, "text": m.text} for m in messages]

    return JsonResponse({"history": history})

@login_required
def chat_view(request):
    user = request.user
    messages = Message.objects.filter(user=user).order_by('timestamp')
    message_list = [{'role': m.role, 'text': m.text} for m in messages]
    return render(request, 'chat.html', {'messages': message_list})

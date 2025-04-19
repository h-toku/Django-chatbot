from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import re
from .models import Message, Conversation
from .utils import generate_text

def home(request):
    return render(request, 'chatbot/home.html')

def get_prompt_from_history(session_id, latest_user_input, max_messages=10):
    """履歴からプロンプトを生成する"""
    messages = Message.objects.filter(session_id=session_id).order_by('-timestamp')[:max_messages][::-1]
    lines = []

    if messages:
        for m in messages:
            role = "ユーザー" if m.role == "user" else "AI"
            lines.append(f"{role}: {m.text}")
    lines.append(f"ユーザー: {latest_user_input}")
    lines.append("AI:")
    return "\n".join(lines)

def chat(request):
    """チャットの主要なビュー"""
    session_id = request.session.session_key or request.session.create()

    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        if not user_input:
            return JsonResponse({"response": "入力が空です。"})
        
        try:
            # プロンプト生成と応答取得
            prompt = get_prompt_from_history(session_id, user_input)
            response = generate_text(prompt)
            response = re.sub(r"http\S+|pic\.twitter\.com/\S+|<unk>", "", response).strip()
            response = re.sub(r'\s+', ' ', response).strip()

            # ログイン時のみ履歴保存
            if request.user.is_authenticated:
                Message.objects.bulk_create([
                    Message(session_id=session_id, role='user', text=user_input),
                    Message(session_id=session_id, role='ai', text=response)
                ])

            return JsonResponse({"response": response})
        except Exception as e:
            return JsonResponse({"response": f"AIエラー: {str(e)}"})

    # GET時の処理
    messages = Message.objects.filter(session_id=session_id).order_by('timestamp') if request.user.is_authenticated else []
    return render(request, 'chatbot/chat.html', {'messages': messages})

@login_required
def chat_history(request):
    """チャット履歴を取得"""
    session_id = request.session.session_key
    if not session_id:
        return JsonResponse({"history": []})

    messages = Message.objects.filter(session_id=session_id).order_by('timestamp')
    history = [{"role": m.role, "text": m.text} for m in messages]
    return JsonResponse({"history": history})

@csrf_exempt
@login_required
def save_conversation(request):
    """会話を保存"""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=400)
    
    try:
        data = json.loads(request.body)
        convo = Conversation.objects.create(
            user=request.user,
            prompt=data.get('prompt'),
            response=data.get('response')
        )
        return JsonResponse({'status': 'success', 'id': convo.id})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
def get_conversation_history(request):
    """保存された会話履歴を取得"""
    conversations = request.user.conversations.order_by('-timestamp')
    data = [{
        'prompt': convo.prompt,
        'response': convo.response,
        'timestamp': convo.timestamp.isoformat()
    } for convo in conversations]
    return JsonResponse({'history': data})
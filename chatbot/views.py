from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
from .models import Conversation, ChatMessage
import logging
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'chatbot/home.html')

def get_prompt_from_history(session_id, latest_user_input, max_messages=10):
    """履歴からプロンプトを生成する"""
    messages = ChatMessage.objects.filter(
        session_id=session_id
    ).order_by('-timestamp')[:max_messages][::-1]
    lines = []

    if messages:
        for m in messages:
            role = "ユーザー" if m.role == "user" else "AI"
            lines.append(f"{role}: {m.message}")
    lines.append(f"ユーザー: {latest_user_input}")
    lines.append("AI:")
    return "\n".join(lines)

def chat_view(request):
    """
    チャット画面を表示するビュー
    """
    # セッションIDの取得または生成
    session_id = request.session.session_key
    if not session_id:
        request.session.save()
        session_id = request.session.session_key

    # チャット履歴の取得
    messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
    chat_history = [{'role': msg.role, 'text': msg.message} for msg in messages]

    return render(request, 'chatbot/chat.html', {
        'chat_history': json.dumps(chat_history),
        'messages': messages
    })

@csrf_exempt
@login_required
@require_http_methods(["POST"])
def chat_api(request):
    """
    チャットAPIのエンドポイント
    """
    try:
        # リクエストボディからJSONデータを取得
        data = json.loads(request.body)
        user_input = data.get('user_input', '').strip()

        if not user_input:
            return JsonResponse({'error': 'メッセージを入力してください'}, status=400)

        # セッションIDの取得または生成
        session_id = request.session.session_key
        if not session_id:
            request.session.save()
            session_id = request.session.session_key

        # ユーザーメッセージの保存
        ChatMessage.objects.create(
            session_id=session_id,
            role='user',
            message=user_input
        )

        # AIの応答を生成（ここでは簡単な応答を返す）
        ai_response = f"あなたのメッセージ: {user_input} を受け取りました。"

        # AIの応答を保存
        ChatMessage.objects.create(
            session_id=session_id,
            role='ai',
            message=ai_response
        )

        return JsonResponse({'response': ai_response})

    except json.JSONDecodeError:
        return JsonResponse({'error': '無効なJSONデータです'}, status=400)
    except Exception as e:
        logger.error(f"チャットAPIエラー: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def chat_history(request):
    """チャット履歴を取得"""
    session_id = request.session.session_key
    if not session_id:
        return JsonResponse({"history": []})

    messages = ChatMessage.objects.filter(session_id=session_id).order_by('timestamp')
    history = [{"role": m.role, "text": m.message} for m in messages]
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

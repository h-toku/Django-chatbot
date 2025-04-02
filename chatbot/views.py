from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from transformers import pipeline

# Hugging Face のチャットボットモデルをロード
chatbot_pipeline = pipeline("text-generation", model="microsoft/DialoGPT-medium")

@csrf_exempt
def chat(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("message", "")

        # モデルで応答を生成
        response = chatbot_pipeline(user_input, max_length=100)[0]['generated_text']

        return JsonResponse({"response": response})

    return JsonResponse({"error": "Invalid request"}, status=400)

# ✅ 追加するべき関数（この関数がないと `NameError` になる）
def chat_page(request):
    return render(request, "chatbot/chat.html")

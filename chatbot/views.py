from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from transformers import pipeline
from .forms import UserRegisterForm

# Hugging Face のチャットボットモデルをロード
chatbot = pipeline("text-generation", model="gpt2")

def chat_page(request):
    return render(request, 'chatbot/chat.html')

def chat(request):
    print("Request method:", request.method)  # リクエストメソッドを確認
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        print("User input:", user_input)  # ユーザーの入力を確認
        if user_input:
            # モデルにユーザーの入力を渡して応答を生成
            response = chatbot(user_input, max_length=100, num_return_sequences=1)
            print("AI Response:", response)  # AIのレスポンスを確認
            return JsonResponse({"response": response[0]['generated_text']})
        else:
            print("Empty input received")  # 入力が空の場合の処理
            return JsonResponse({"response": "入力が空です。"})
    else:
        print("Invalid request method")  # POST以外のリクエストが来た場合
        return JsonResponse({"response": "Invalid request method"})

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 登録後に自動的にログイン
            return redirect('home')  # ログイン後のリダイレクト先を指定
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})
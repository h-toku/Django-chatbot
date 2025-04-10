from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from .forms import UserRegisterForm
from django.contrib.auth import login

# T5-smallを使用
model_name = "t5-small"

# モデルとトークナイザーの読み込み
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def chat_page(request):
    return render(request, 'chatbot/chat.html')

def chat(request):
    print("Request received:", request.method)
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        print("User input received:", user_input)
        inputs = tokenizer(user_input, return_tensors="pt")

        if user_input:
            try:
                # モデルにユーザーの入力を渡して応答を生成
                outputs = model.generate(inputs["input_ids"], max_length=100, num_return_sequences=1)
                print("Model output:", outputs)
                response = tokenizer.decode(outputs[0])  # skip_special_tokensを外してみる
                print("AI Response:", response)
                return JsonResponse({"response": response.strip()})  # 余計な部分があれば取り除く
            except Exception as e:
                print(f"Error generating response: {e}")
                return JsonResponse({"response": f"AIエラー: {str(e)}"})
        else:
            print("Empty input received")
            return JsonResponse({"response": "入力が空です。"})

    else:
        print("Invalid request method")
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

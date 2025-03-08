import os
import openai
from django.http import JsonResponse
from dotenv import load_dotenv

#.envファイルを読み込む
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def chat(request):
    user_message = request.GET.get("message", "")

    if not user_message:
        return JsonResponse({"error":"メッセージを入力してください。"},status=400)
    
    response = openai.ChatCompletion.create(model="gpt-4", messages=[{"role":"user", "contnt": user_message}])

    ai_message = response["choices"][0]["message"]["content"]
    return JsonResponse({"response": ai_message})
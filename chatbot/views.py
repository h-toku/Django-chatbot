from django.shortcuts import render
from django.http import JsonResponse
import re
from transformers import AutoModelForCausalLM, AutoTokenizer
from django.contrib.auth.decorators import login_required

# T5-smallを使用
model_name = "rinna/japanese-gpt2-small"

tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(model_name)

def chat_page(request):
    return render(request, 'chatbot/chat.html')

def chat(request):
    print("Request received:", request.method)
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '')
        print("User input received:", user_input)
        inputs = tokenizer(user_input, return_tensors="pt")
        input_ids = inputs["input_ids"]
        attention_mask = inputs["attention_mask"]

        if user_input:
            try:
                # モデルにユーザーの入力を渡して応答を生成
                outputs = model.generate(
                    input_ids,
                    attention_mask=attention_mask,
                    num_return_sequences=1,
                    pad_token_id=tokenizer.eos_token_id,
                    no_repeat_ngram_size=2,  # 同じn-gramの繰り返しを防ぐ
                    repetition_penalty=1.3,  # 繰り返しへのペナルティ
                    top_p=0.95,              # nucleus sampling（多様性）
                    top_k=50,                # トークンの上位50から選ぶ（多様性）
                    temperature=1.0          # 出力のランダム性
                )
                print("Model output:", outputs)
                response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                response = re.sub(r"http\S+|pic\.twitter\.com/\S+|<unk>", "", response) 
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

@login_required
def chat_view(request):
    return render(request, 'chat/chat.html')

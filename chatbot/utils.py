import requests
import os

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/rinna/japanese-gpt-neox-3.6b"
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")  # ←ここにアクセストークンを記載（.env化推奨）

headers = {
    "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
}

def query_huggingface(prompt: str):
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": 100}
    }
    response = requests.post(HUGGINGFACE_API_URL, headers=headers, json=payload)
    response.raise_for_status()
    result = response.json()
    return result[0]['generated_text']

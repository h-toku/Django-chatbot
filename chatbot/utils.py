from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
import re

logger = logging.getLogger(__name__)

def load_model_and_tokenizer():
    try:
        model_name = "rinna/japanese-gpt2-medium"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # GPUが利用可能な場合はGPUを使用、それ以外はCPUを使用
        device = "cuda" if torch.cuda.is_available() else "cpu"
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        ).to(device)
        
        return model, tokenizer
    
    except Exception as e:
        logger.error(f"モデルのロード中にエラーが発生: {e}")
        raise

def clean_input(text: str) -> str:
    """入力テキストをクリーンアップする"""
    # 特殊文字と余分な空白を削除
    text = re.sub(r'[「」『』【】()（）［］\[\]]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_text(prompt: str, max_length: int = 100):
    try:
        model, tokenizer = load_model_and_tokenizer()

        cleaned_prompt = re.sub(r'(ユーザー:|AI:)', '', clean_input(prompt))
        
        inputs = tokenizer(cleaned_prompt, return_tensors="pt").to(model.device)

        logger.error(f"cleaned_prompt: {cleaned_prompt}")
        logger.error(f"Inputs: {inputs}")
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=True,
                temperature=0.8,          # より多様な応答を促進
                top_p=0.92,              # より自然な文章生成
                top_k=50,                # トップKサンプリングを追加
                repetition_penalty=1.5,   # 繰り返しペナルティを強化
                no_repeat_ngram_size=4,   # より長いフレーズの繰り返しを防止
                length_penalty=1.2,       # より適切な長さの応答を促進
                pad_token_id=tokenizer.eos_token_id,
                bos_token_id=tokenizer.bos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                num_return_sequences=1,
                early_stopping=True
            )

        input_length = inputs['input_ids'].shape[1]

        logger.error(f"outputs: {outputs}")
        generated_text = tokenizer.decode(outputs[0][input_length:], skip_special_tokens=True)
        logger.error(f"Generated text: {generated_text}")
        # 不要なトークンやURLを削除
        return generated_text

    except Exception as e:
        logger.error(f"テキスト生成中にエラーが発生: {e}")
        return f"モデルの処理中にエラーが発生しました: {str(e)}"
    

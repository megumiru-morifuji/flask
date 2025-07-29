from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GAS_WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbwLw3dZZau-lhAywa7Z-CQVJtMrAwouQ6C8ybGmYGqQfB-uzYS5PUSWY0O-qm2xPxdv/exec'

# ✅ 翻訳結果をGASに返す関数
def send_translation_back_to_gas(original_text, translated_text):
    import json
    headers = {
        'Content-Type': 'application/json'
    }
    data = json.dumps({
        'originalText': original_text,
        'translatedText': translated_text
    })
    response = requests.post(GAS_WEB_APP_URL, headers=headers, data=data)
    return response.status_code

@app.route("/translate", methods=["POST"])
def translate():
    data = request.get_json()
    print("Data received:", data)
    text = data.get("text")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    # ✅ Gemini APIに翻訳リクエスト
    gemini_url = (
    "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent"
    f"?key={GEMINI_API_KEY}"
    )

    headers = {"Content-Type": "application/json"}
    payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": (
                        "以下の日本語テキストを、eBayの商品紹介文として英語に翻訳してください。\n"
                        "- 原文の意味やニュアンスをできるだけ忠実に保つこと\n"
                        "- 不要な脚色や事実に反する追加表現を避けること\n"
                        "- 英語として不自然にならない程度に表現を整えること\n"
                        "- 商品紹介にふさわしい、読み手に伝わりやすく、親しみやすいトーンにすること\n"
                        "- 読者に語りかけるような自然な英文にすること（This item is... / Perfect for... など）\n"
                        "- 可能であれば商品の魅力や用途が伝わるような一文も加えること\n"
                        "- 翻訳結果のみを出力してください。解説や複数候補は不要です。\n"
                        "- 原文が複数文なら、英語も複数文にしてください。\n\n"
                        f"日本語テキスト: {text}"
                        )
                    }
                ]
            }
        
    }

    response = requests.post(gemini_url, json=payload, headers=headers)
    if response.status_code != 200:
        return jsonify({"error": "Gemini API failed", "details": response.text}), 500

    gemini_response = response.json()
    translation = gemini_response['candidates'][0]['content']['parts'][0]['text']

    # ✅ 翻訳結果をGASに送信
    send_translation_back_to_gas(text, translation)

    return jsonify({"translation": translation})

if __name__ == "__main__":
    app.run(debug=True)

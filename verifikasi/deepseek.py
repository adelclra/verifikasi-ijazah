import requests
import os

def validate_year_with_deepseek(text):
    api_key = os.getenv("DEEPSEEK_API_KEY")

    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "user",
                "content": (
                    "Dari teks berikut, ambil TAHUN ijazah saja. "
                    "Jawab hanya dengan angka tahun (contoh: 2023). "
                    "Jika tidak ada tahun, jawab: TIDAK ADA.\n\n"
                    f"{text}"
                )
            }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)
    data = response.json()

    try:
        return data["choices"][0]["message"]["content"].strip()
    except:
        return "TIDAK ADA"

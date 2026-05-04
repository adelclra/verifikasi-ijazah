import requests
import os

API_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_with_qwen(text):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "qwen/qwen3-next-80b-a3b-instruct",
                "messages": [
                    {
                        "role": "system",
                        "content": "Kamu adalah AI untuk membaca teks hasil OCR ijazah."
                    },
                    {
                        "role": "user",
                        "content": f"""
Ambil NAMA SISWA dari teks berikut.

Perbaiki ejaan jika ada kesalahan OCR.

Balas hanya nama lengkap saja tanpa kata lain.

Teks:
{text[:2000]}
"""
                    }
                ],
                "temperature": 0.2
            },
            timeout=30
        )

        data = response.json()
        print("\n=== QWEN RAW RESPONSE ===\n", data)

        if "choices" in data:
            result = data["choices"][0]["message"]["content"].strip()

            if result.lower() == "null":
                return None

            return result

        print("QWEN FORMAT ERROR:", data)
        return None

    except Exception as e:
        print("QWEN ERROR:", e)
        return None
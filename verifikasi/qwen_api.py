import requests
import os

API_KEY = os.getenv("OPENROUTER_API_KEY")


def extract_with_qwen(text):

    try:

        if not text:
            print("QWEN: OCR kosong")
            return None

        if len(text.strip()) < 20:
            print("QWEN: OCR terlalu pendek")
            return None

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
                        "content": """Anda adalah AI pembaca hasil OCR ijazah Indonesia.

TUGAS UTAMA:
Ekstrak NAMA LENGKAP SISWA dari hasil OCR ijazah.

ATURAN PENTING:
1. Ambil HANYA nama siswa/peserta didik.
2. JANGAN ambil nama kepala sekolah, orang tua, atau nama sekolah.
3. Nama siswa biasanya muncul setelah kata: "nama", "menerangkan bahwa", "bahwa", "kepada", "peserta didik".

PERBAIKAN OCR:
OCR sering MEMECAH satu kata menjadi beberapa fragmen. Contoh kesalahan umum:
- "Imm An El" seharusnya "Immanuel"
- "Sab In" seharusnya "Sabin" atau "Sabina"  
- "Eli Zab Eth" seharusnya "Elizabeth"

ANDA HARUS:
- Gabungkan fragmen-fragmen yang terpecah menjadi nama yang benar
- Perbaiki huruf yang terpotong di akhir kata (misal "Sabin" -> "Sabina" jika konteks menunjukkan demikian)
- Gunakan pengetahuan nama Indonesia/Manado/Minahasa untuk memperbaiki nama
- Nama Minahasa/Manado umum: Ticoalu, Sumajow, Rumuat, Pasanda, Massie, Tumewu, Wowor, Mamahit, Rantung, Lumenta, dll.

FORMAT JAWABAN:
Balas HANYA dalam format JSON, tanpa teks lain:
{"nama": "Nama Lengkap Siswa", "tahun": "2022"}

Jika tahun tidak ditemukan, isi null:
{"nama": "Nama Lengkap Siswa", "tahun": null}

Jika nama tidak ditemukan sama sekali:
{"nama": null, "tahun": null}

JANGAN tambahkan penjelasan apapun. HANYA JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"""Ekstrak nama siswa dari OCR ijazah berikut.

OCR:
{text[:4000]}"""
                    }
                ],
                "temperature": 0.05,
                "max_tokens": 100
            },
            timeout=60
        )

        data = response.json()

        print("\n=== QWEN RAW RESPONSE ===\n", data)

        if "choices" not in data:
            print("QWEN FORMAT ERROR:", data)
            return None

        result = data["choices"][0]["message"]["content"].strip()

        print("\n=== QWEN RESULT ===\n")
        print(result)

        import re
        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()

        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result = json_match.group(0)

        if result.upper() == "NULL":
            return None

        if len(result) < 3:
            return None

        return result

    except Exception as e:

        print("QWEN ERROR:", e)

        return None
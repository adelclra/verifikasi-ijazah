import requests
import re
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

Ekstrak NAMA LENGKAP SISWA dan TAHUN dari hasil OCR ijazah.

STRUKTUR IJAZAH INDONESIA:
1. Header: "KEMENTERIAN PENDIDIKAN...", "IJAZAH", "SEKOLAH MENENGAH ATAS"
2. "TAHUN AJARAN 20XX/20XX"
3. "Kepala [nama sekolah]" — ABAIKAN
4. "menerangkan bahwa:" lalu "nama :" — NAMA SISWA ADA DI SINI
5. "tempat dan tanggal lahir :" — ABAIKAN
6. "nama orang tua/wali :" — BUKAN nama siswa, tapi PETUNJUK MARGA

ATURAN:
1. Ambil HANYA nama siswa (setelah "nama :" dan sebelum "tempat")
2. JANGAN ambil nama kota, sekolah, kepala sekolah, atau orang tua
3. Periksa "nama orang tua/wali" — marga orang tua SAMA dengan marga siswa

KOREKSI OCR — SANGAT PENTING:
OCR sering membuat kesalahan berikut pada nama:
- "ADEAIA" seharusnya "ADELIA" (huruf L dan I terbaca A)
- "FEAICIA" seharusnya "FELICIA"
- "ANCEAA" seharusnya "ANGELA"
- "PATRTCTA" seharusnya "PATRICIA"
- Huruf dipisah titik: "S.A.N.C.I.A" → gabung jadi "SANCIA"
- Fragmen kata: "A.LIC.A" → gabung jadi "ALICA"
- "J" dan "V" sering tertukar
- "l" dan "i" dan "1" sering tertukar
- "rn" terbaca "m", "cl" terbaca "d"
- Huruf pertama marga kadang hilang: "Angitan" → "Langitan"

ATURAN KOREKSI:
1. Gabungkan huruf/fragmen yang dipisah titik menjadi SATU KATA
2. Cocokkan dengan nama Indonesia yang umum dan perbaiki ejaannya
3. Marga siswa = marga orang tua — gunakan ejaan orang tua jika lebih jelas
4. Jika nama terlihat salah tapi mirip nama umum, PERBAIKI ke nama yang benar
5. Nama yang umum di Sulawesi Utara: Langitan, Manoppo, Pangkey, Rompas, Sondakh, Tendean, Tumbelaka, Wenas, Wowor, Kalangi, Kaunang, dll.

TAHUN:
- Ambil tahun terakhir dari "TAHUN AJARAN 20XX/20XX"
- Atau tahun dari tanggal penerbitan ijazah

FORMAT JAWABAN (HANYA JSON, tanpa penjelasan):
{"nama": "Nama Lengkap Siswa Yang Sudah Dikoreksi", "tahun": "2024"}

Jika tidak ditemukan:
{"nama": null, "tahun": null}"""
                    },
                    {
                        "role": "user",
                        "content": f"Ekstrak nama siswa dan tahun dari OCR ijazah berikut. WAJIB koreksi kesalahan OCR pada nama.\n\nOCR:\n{text[:4000]}"
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
        print(f"\n=== QWEN RESULT === {result}")

        result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()

        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result = json_match.group(0)

        if result.upper() == "NULL" or len(result) < 3:
            return None

        return result

    except requests.exceptions.Timeout:
        print("QWEN TIMEOUT: menggunakan fallback")
        return None

    except Exception as e:
        print("QWEN ERROR:", e)
        return None
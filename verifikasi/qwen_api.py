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

Tugas Anda: mengekstrak NAMA LENGKAP SISWA dan TAHUN dari hasil OCR ijazah.

STRUKTUR IJAZAH INDONESIA:
1. Header: "KEMENTERIAN PENDIDIKAN...", "IJAZAH", "SEKOLAH MENENGAH ATAS"
2. "TAHUN AJARAN 20XX/20XX"s
3. "Kepala [nama sekolah]" — ABAIKAN
4. "menerangkan bahwa:" lalu "nama :" — NAMA SISWA ADA DI SINI
5. "tempat dan tanggal lahir :" — ABAIKAN
6. "nama orang tua/wali :" — BUKAN nama siswa, tapi PETUNJUK MARGA siswa

ATURAN PENGAMBILAN NAMA:
1. Nama siswa berada di sekitar kata "nama" dan sebelum "tempat dan tanggal lahir"
2. PENTING: karena OCR membaca secara horizontal, nama siswa bisa muncul SEBELUM atau SESUDAH label "nama :"
3. Nama siswa adalah nama orang (2-5 kata), BUKAN nama tempat atau tanggal
4. Jika teks antara "nama" dan "tempat" terlihat seperti nama kota atau tanggal, cari nama orang di SEBELUM kata "nama"
5. Gunakan marga orang tua sebagai petunjuk: marga siswa biasanya sama dengan marga orang tua
6. JANGAN ambil nama kota, sekolah, kepala sekolah, atau orang tua sebagai nama siswa

PEMBERSIHAN ARTEFAK OCR (WAJIB):
- Huruf yang dipisah titik adalah SATU KATA. Gabungkan: "S.A.N.C.I.A" menjadi "SANCIA", "A.L.CI.A" menjadi "ALCIA"
- Hapus semua titik di antara huruf dalam nama
- Pisahkan kata-kata yang seharusnya terpisah berdasarkan konteks: "SANCIAALCIA" seharusnya "SANCIA ALCIA"
- Hapus karakter non-huruf yang bukan pemisah kata

KOREKSI HURUF TUNGGAL YANG SERING KELIRU DI OCR:
- "l" (huruf L kecil) dan "I" (huruf i besar) sering tertukar
- "V" dan "J" sering tertukar  
- "rn" terbaca "m"
- "cl" terbaca "d"
- "c" terbaca "l"
Perbaiki HANYA jika konteks huruf sekitarnya jelas menunjukkan kesalahan. Jika ragu, PERTAHANKAN huruf asli.

PENGGUNAAN MARGA ORANG TUA:
- Marga siswa biasanya SAMA dengan marga orang tua/wali
- Jika marga siswa terbaca tidak jelas tapi marga orang tua terbaca jelas, gunakan ejaan marga orang tua untuk marga siswa
- Contoh: siswa terbaca "CANGITAN", orang tua terbaca "Langitan" → marga siswa = "LANGITAN"

LARANGAN — JANGAN LAKUKAN INI:
- JANGAN mengganti nama depan/tengah siswa ke nama lain yang "terdengar lebih umum"
- JANGAN menebak nama yang tidak terbaca — jika benar-benar tidak bisa dibaca, tulis apa adanya
- "ADEAIA" BUKAN "ADELIA" kecuali konteks huruf sekitarnya sangat jelas menunjukkan itu huruf L dan I
- "MIRACLE" BUKAN "MICHAEL" — ini nama yang berbeda, jangan ganti
- "SABINA" BUKAN "SANCIA" — ini nama yang berbeda, jangan ganti

TAHUN:
- Ambil tahun terakhir dari "TAHUN AJARAN 20XX/20XX"
- Atau tahun dari tanggal penerbitan ijazah

FORMAT JAWABAN (HANYA JSON, tanpa penjelasan):
{"nama": "Nama Lengkap Siswa", "tahun": "2024"}

Jika tidak ditemukan:
{"nama": null, "tahun": null}"""
                    },
                    {
                        "role": "user",
                        "content": f"Ekstrak nama siswa dan tahun dari OCR ijazah berikut.\n\nOCR:\n{text[:4000]}"
                    }
                ],
                "temperature": 0,
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
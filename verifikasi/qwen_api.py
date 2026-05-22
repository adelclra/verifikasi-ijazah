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
Ekstrak NAMA LENGKAP SISWA dan TAHUN dari hasil OCR ijazah.

STRUKTUR UMUM IJAZAH INDONESIA:
1. Header: "KEMENTERIAN PENDIDIKAN...", "IJAZAH", "SEKOLAH MENENGAH ATAS"
2. "TAHUN AJARAN 20XX/20XX"
3. "Kepala [nama sekolah]" — ABAIKAN
4. Nomor Pokok Sekolah, Kabupaten/Kota, Provinsi — ABAIKAN
5. "menerangkan bahwa:" lalu "nama :" — NAMA SISWA ADA DI SINI
6. "tempat dan tanggal lahir :" — ABAIKAN
7. "nama orang tua/wali :" — INI BUKAN NAMA SISWA, tapi WAJIB dipakai sebagai PETUNJUK MARGA

ATURAN KETAT:
1. Ambil HANYA nama siswa (setelah "nama :" dan sebelum "tempat dan tanggal lahir")
2. JANGAN ambil nama kota, sekolah, kepala sekolah, atau orang tua sebagai nama siswa
3. WAJIB periksa bagian "nama orang tua/wali" — marga di sana biasanya SAMA dengan marga siswa. Jika marga orang tua terbaca lebih jelas, GUNAKAN ejaan tersebut untuk memperbaiki marga siswa yang terpecah atau salah baca oleh OCR

PERBAIKAN OCR — INI SANGAT PENTING:
OCR pada ijazah sering memecah kata dengan titik-titik atau spasi karena format dokumen.

Kesalahan umum:
- Huruf dipisah titik: misal "S.A.N.C.I.A" seharusnya digabung jadi satu kata
- Fragmen kata: misal "A.LIC.A" seharusnya digabung jadi satu kata utuh
- Marga terpecah: fragmen huruf yang dipisah titik di akhir nama adalah SATU KATA MARGA, bukan dua kata terpisah
- Awalan marga hilang: huruf pertama marga kadang tidak terbaca oleh OCR
- Huruf salah baca: "J" dan "V" sering tertukar, "l" dan "i" sering tertukar, "rn" terbaca "m", "cl" terbaca "d"
- Nama umum harus dikoreksi: OCR sering salah baca nama yang sebenarnya umum, perbaiki ke ejaan yang benar
- Huruf tambahan: OCR kadang menambah huruf ekstra di akhir kata, hapus jika tidak masuk akal

ATURAN KOREKSI NAMA:
1. Gabungkan semua huruf/fragmen yang dipisah titik menjadi SATU KATA
2. Marga siswa biasanya SAMA dengan marga orang tua/wali — gunakan ini untuk koreksi ejaan
3. Jika marga orang tua terbaca lebih jelas, gunakan ejaan tersebut untuk nama siswa
4. Marga Indonesia umumnya adalah SATU KATA — jangan pecah jadi dua kata terpisah
5. Jika fragmen marga siswa mirip tapi tidak identik dengan marga orang tua, PRIORITASKAN ejaan dari marga orang tua
6. Perbaiki nama depan dan tengah yang salah baca ke nama yang umum dan masuk akal
7. Jika ada huruf tambahan yang tidak masuk akal di akhir nama, hapus

TAHUN:
- Ambil tahun terakhir dari "TAHUN AJARAN 20XX/20XX" (ambil yang kedua)
- Atau tahun dari tanggal penerbitan ijazah
- Format: 4 digit angka

FORMAT JAWABAN:
Balas HANYA dalam format JSON:
{"nama": "Nama Lengkap Siswa", "tahun": "2024"}

Jika tidak ditemukan:
{"nama": null, "tahun": null}

JANGAN tambahkan penjelasan. HANYA JSON."""
                    },
                    {
                        "role": "user",
                        "content": f"""Ekstrak nama siswa dan tahun dari OCR ijazah berikut.

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
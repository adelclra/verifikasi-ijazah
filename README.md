# Sistem Verifikasi Tahun Ijazah Berbasis Web
## REGMABA UNSRAT

Sistem ini merupakan aplikasi berbasis web yang digunakan untuk melakukan verifikasi tahun ijazah secara otomatis menggunakan teknologi OCR (Optical Character Recognition) pada Sistem REGMABA Universitas Sam Ratulangi.

Pengguna dapat mengunggah ijazah (gambar/PDF), kemudian sistem akan mengekstraksi nama dan tahun secara otomatis. Hasil tersebut akan diverifikasi oleh admin untuk menentukan validitas dokumen.

---

## Fitur Utama

- Upload multi-file ijazah (gambar JPG/PNG dan PDF)
- Ekstraksi nama dan tahun menggunakan PaddleOCR + Qwen AI
- Hasil upload muncul secara real-time (AJAX per-file)
- Dashboard admin dengan statistik lengkap
- Metrik akurasi OCR: CER (Character Error Rate) dan WER (Word Error Rate)
- Verifikasi oleh admin (Valid / Tidak Memenuhi Syarat)
- Edit data hasil OCR oleh admin
- Visualisasi data (Chart.js - Bar & Doughnut)
- Ekspor laporan ke PDF (ReportLab) dan Excel (openpyxl)
- Search, filter status, dan pagination
- Halaman pengaturan admin (edit profil, ubah password)
- Responsive design

---

## Teknologi yang Digunakan

- **Backend**: Django 5.x (Python)
- **Frontend**: HTML, CSS, JavaScript
- **OCR**: PaddleOCR (lang: id)
- **AI**: Qwen (via OpenRouter API) untuk koreksi nama
- **Preprocessing**: OpenCV (grayscale, denoise, CLAHE)
- **Metrik**: Levenshtein Distance (CER & WER)
- **Chart**: Chart.js
- **Ekspor PDF**: ReportLab
- **Ekspor Excel**: openpyxl
- **Database**: SQLite

---

## Alur Sistem

1. Pengguna mengunggah file ijazah (gambar/PDF)
2. Sistem melakukan preprocessing (resize, grayscale, denoise, CLAHE)
3. PaddleOCR membaca teks dari gambar
4. Qwen AI mengekstraksi nama siswa dan memperbaiki fragmentasi OCR
5. Sistem mendeteksi tahun dari teks OCR
6. Hasil ditampilkan secara real-time ke pengguna
7. Admin memverifikasi dan mengoreksi data jika perlu
8. Sistem menghitung CER dan WER setelah admin mengoreksi
9. Laporan dapat diekspor ke PDF/Excel

---

## Cara Menjalankan

### 1. Clone Repository
```bash
git clone <repo-url>
cd verifikasi_ijazah
```

### 2. Buat Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Environment
Buat file `.env` di root project:
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
OPENROUTER_API_KEY=your-openrouter-api-key

### 5. Migrasi Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Buat Superuser
```bash
python manage.py createsuperuser
```

### 7. Jalankan Server
```bash
python manage.py runserver
```

### 8. Akses Aplikasi
- Halaman Upload: http://127.0.0.1:8000/
- Login Admin: http://127.0.0.1:8000/login/
- Dashboard: http://127.0.0.1:8000/dashboard/

---
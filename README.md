# 🎓 Sistem Verifikasi Ijazah Berbasis OCR

Sistem ini merupakan aplikasi berbasis web yang digunakan untuk melakukan verifikasi ijazah secara otomatis menggunakan teknologi OCR (Optical Character Recognition).

Mahasiswa dapat mengunggah ijazah (gambar/PDF), kemudian sistem akan mengekstraksi informasi tahun secara otomatis. Hasil tersebut akan diverifikasi oleh admin untuk menentukan validitas dokumen.

---

## 🚀 Fitur Utama

- 📤 Upload ijazah (gambar/PDF)
- 🔍 Ekstraksi tahun menggunakan OCR
- 📊 Status otomatis:
  - Menunggu Verifikasi
  - Tidak Terdeteksi
- 👨‍💻 Verifikasi oleh admin:
  - Valid
  - Tidak Memenuhi Syarat
- 📈 Dashboard admin (statistik & monitoring)
- 🔎 Search, filter, dan pagination
- 📊 Visualisasi data (Chart.js)
- 📄 Export laporan:
  - PDF
  - Excel

---

## 🧠 Alur Sistem

1. Mahasiswa mengunggah ijazah
2. Sistem menyimpan file
3. OCR membaca tahun ijazah
4. Sistem menentukan status awal
5. Status ditampilkan ke mahasiswa
6. Admin melakukan verifikasi
7. Sistem menyimpan hasil verifikasi
8. Hasil ditampilkan ke mahasiswa & admin

---

## 🛠️ Teknologi yang Digunakan

- **Backend**: Django (Python)
- **Frontend**: HTML, CSS, JavaScript
- **OCR**: Tesseract / Library OCR
- **Chart**: Chart.js
- **Database**: SQLite (development)

---

## ⚙️ Cara Menjalankan Project

### 1. Clone Repository
```bash
git clone https://github.com/username/verifikasi-ijazah.git
cd verifikasi-ijazah

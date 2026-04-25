import cv2
import pytesseract
import re
import os
import pdfplumber
from datetime import datetime
from .pdf_utils import pdf_to_images

# =========================
# KONFIGURASI TESSERACT
# =========================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


# ======================================================
# EKSTRAKSI TEXT DARI GAMBAR (OCR)
# ======================================================
def extract_text_from_image(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(
        gray, 0, 255,
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    text = pytesseract.image_to_string(
        gray,
        lang="ind+eng",
        config="--psm 6"
    )

    return text


# ======================================================
# EKSTRAKSI TEXT DARI PDF
# ======================================================
def extract_text_from_pdf(file_path):
    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except:
        pass

    return text


# ======================================================
# EKSTRAKSI TAHUN (RULE-BASED)
# ======================================================
def extract_year_from_text(text):
    text = text.upper()

    # ======================
    # 1. PRIORITAS: TAHUN AJARAN / PELAJARAN
    # ======================
    match = re.search(
        r"TAHUN\s+(AJARAN|PELAJARAN)\s+(\d{4})\s*/\s*(\d{4})",
        text
    )
    if match:
        start_year = int(match.group(2))
        end_year = int(match.group(3))

        # 🔥 Perbaikan error OCR (misal 2022/2025 → 2023)
        if end_year != start_year + 1:
            end_year = start_year + 1

        return str(end_year)

    # ======================
    # 2. PRIORITAS: TANGGAL (FILTER)
    # ======================
    match = re.search(
        r"(KOTA|TANGGAL)[^\n]*?(\d{1,2})\s+(JANUARI|FEBRUARI|MARET|APRIL|MEI|JUNI|JULI|AGUSTUS|SEPTEMBER|OKTOBER|NOVEMBER|DESEMBER)\s+(20\d{2})",
        text
    )
    if match:
        return match.group(4)

    # ======================
    # 3. FALLBACK
    # ======================
    candidates = re.findall(r"\b(20\d{2})\b", text)

    if not candidates:
        return None

    candidates = [int(y) for y in candidates]

    current_year = datetime.now().year

    valid_years = [
        y for y in candidates
        if 2018 <= y <= current_year
    ]

    if valid_years:
        return str(max(valid_years))

    return None


# ======================================================
# FUNGSI UTAMA
# ======================================================
def extract_year(file_path):
    text = ""

    # ======================
    # 1. CEK PDF
    # ======================
    if file_path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(file_path)

        # kalau PDF tidak ada text → OCR
        if len(text.strip()) < 20:
            images = pdf_to_images(file_path)
            for img_path in images:
                img = cv2.imread(img_path)
                if img is not None:
                    text += extract_text_from_image(img)

    # ======================
    # 2. CEK GAMBAR
    # ======================
    else:
        img = cv2.imread(file_path)
        if img is not None:
            text = extract_text_from_image(img)

    # ======================
    # DEBUG OUTPUT
    # ======================
    print("\n\n================ OCR RESULT ================\n")
    print(text)
    print("\n===========================================\n")

    # ======================
    # EKSTRAKSI TAHUN
    # ======================
    year = extract_year_from_text(text)

    return year, text
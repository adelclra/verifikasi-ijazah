import cv2
import re
import os
import json
import numpy as np

from .pdf_utils import pdf_to_images
from .qwen_api import extract_with_qwen


# =========================
# INIT PADDLE OCR 
# =========================
_ocr_instance = None

def get_ocr():
    global _ocr_instance
    if _ocr_instance is None:
        from paddleocr import PaddleOCR
        _ocr_instance = PaddleOCR(
            use_angle_cls=True,
            lang='id',
            det_db_thresh=0.3,
            det_db_box_thresh=0.5,
            show_log=False,
        )
    return _ocr_instance


# =========================
# KNOWN CITY NAMES
# =========================
KNOWN_CITIES = {
    "tomohon", "manado", "bitung", "jakarta", "surabaya", "bandung",
    "medan", "makassar", "semarang", "yogyakarta", "palembang",
    "tangerang", "depok", "bekasi", "bogor", "malang", "solo",
    "pontianak", "banjarmasin", "balikpapan", "samarinda", "kendari",
    "ambon", "jayapura", "kupang", "mataram", "denpasar", "gorontalo",
    "ternate", "manokwari", "sorong", "palu", "mamuju", "tondano",
    "langowan", "airmadidi", "amurang", "kotamobagu", "minahasa",
}


# =========================
# PREPROCESS
# =========================
def preprocess(image):
    try:
        h, w = image.shape[:2]
        target_width = 2000
        max_width = 2500

        if w < target_width:
            scale = target_width / w
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        elif w > max_width:
            scale = max_width / w
            image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        denoised = cv2.fastNlMeansDenoising(
            gray, h=10, templateWindowSize=7, searchWindowSize=21
        )

        clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)

        kernel = np.array([[0, -1, 0],
                           [-1, 5.5, -1],
                           [0, -1, 0]])
        sharpened = cv2.filter2D(enhanced, -1, kernel)

        result = cv2.cvtColor(sharpened, cv2.COLOR_GRAY2BGR)
        return result

    except Exception as e:
        print("PREPROCESS ERROR:", e)
        return image


# =========================
# CLEAN TEXT
# =========================
def clean(text):
    text = re.sub(r"[^A-Za-z0-9\s/.,:]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# DETECT DOC TYPE
# =========================
def detect_document_type(text):
    text = text.upper()
    if "DAFTAR NILAI" in text:
        return "nilai"
    elif "IJAZAH" in text:
        return "ijazah"
    return "unknown"


# =========================
# EXTRACT YEAR
# =========================
def extract_year(text):
    text = text.upper()
    match = re.search(r"(20\d{2})\s*/\s*(20\d{2})", text)
    if match:
        return match.group(2)
    candidates = re.findall(r"\b20\d{2}\b", text)
    if candidates:
        return str(max(map(int, candidates)))
    return None


# =========================
# CLEAN NAME
# =========================
def clean_name(name):
    if not name:
        return None

    name = re.sub(r"[^A-Za-z\s]", "", name)
    words = name.split()

    words = [
        w for w in words
        if len(w) >= 2 and w.lower() not in KNOWN_CITIES
    ]

    if not words:
        return None

    return " ".join(words[:6]).title()


# =========================
# VALIDATE NAME
# =========================
def is_valid_name(name):
    if not name:
        return False
    if len(name) < 3:
        return False
    if not re.search(r'[A-Za-z]{2,}', name):
        return False
    return True


# =========================
# FALLBACK NAME EXTRACTION
# =========================
def extract_name_between_markers(text):
    text = text.upper().replace("\n", " ")

    patterns = [
        r"NAMA\s*[:/]?\s*([A-Z\s]{5,})\s*TEMPAT",
        r"BAHWA\s+([A-Z\s]{5,})\s+TEMPAT",
        r"ATAS NAMA\s+([A-Z\s]{5,})\s+LAHIR",
        r"MENERANGKAN\s+BAHWA\s+([A-Z\s]{5,})",
    ]

    blacklist = {"ORANG TUA", "WALI", "KEPALA", "SEKOLAH", "PROVINSI",
                 "KABUPATEN", "TEMPAT", "TANGGAL", "LAHIR", "DAN"}

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            candidate = match.group(1)
            candidate = re.sub(r"[^A-Z\s]", "", candidate)

            if any(bl in candidate for bl in blacklist):
                continue

            words = candidate.split()
            words = [w for w in words if len(w) >= 2]
            if len(words) >= 2:
                return " ".join(words[:6]).title()

    return None


# =========================
# PARSE QWEN RESULT
# =========================
def parse_qwen_result(ai_result):
    if not ai_result:
        return None, None

    try:
        data = json.loads(ai_result)
        nama = data.get("nama")
        tahun = data.get("tahun")
        return (nama, tahun)
    except:
        cleaned = ai_result.strip()
        for prefix in ["Nama Siswa:", "NAMA SISWA:", "Nama:", "NAMA:"]:
            if cleaned.upper().startswith(prefix.upper()):
                cleaned = cleaned[len(prefix):].strip()

        if cleaned.upper() == "NULL":
            return None, None
        if len(cleaned) >= 3:
            return cleaned, None
        return None, None


# =========================
# OCR USING PADDLE
# =========================
def paddle_ocr_text(image):
    try:
        result = get_ocr().ocr(image, cls=True)
        full_text = ""

        if not result or not result[0]:
            return ""

        lines = sorted(result[0], key=lambda x: x[0][0][1])

        for line in lines:
            try:
                text = line[1][0]
                confidence = line[1][1]
                if confidence < 0.5:
                    continue
                full_text += text + " "
            except:
                continue

        return clean(full_text)

    except Exception as e:
        print("PADDLE OCR ERROR:", e)
        return ""


# =========================
# OCR WITH LINE STRUCTURE
# =========================
def paddle_ocr_structured(image):
    try:
        result = get_ocr().ocr(image, cls=True)

        if not result or not result[0]:
            return ""

        lines = sorted(result[0], key=lambda x: x[0][0][1])
        structured = []

        for line in lines:
            try:
                text = line[1][0]
                confidence = line[1][1]
                y_pos = int(line[0][0][1])
                if confidence < 0.4:
                    continue
                structured.append(f"[Y={y_pos}] {text}")
            except:
                continue

        return "\n".join(structured)

    except Exception as e:
        print("PADDLE OCR STRUCTURED ERROR:", e)
        return ""


# =========================
# MAIN FUNCTION
# =========================
def extract_data(file_path):
    try:
        image = None

        if file_path.lower().endswith(".pdf"):
            images = pdf_to_images(file_path)
            if images and len(images) > 0:
                image = cv2.imread(images[0])
        else:
            image = cv2.imread(file_path)

        if image is None:
            print("Gagal membaca gambar")
            return ("Tidak Terdeteksi", None, "")

        processed_image = preprocess(image)

        text_full = paddle_ocr_text(processed_image)
        text_structured = paddle_ocr_structured(processed_image)

        print("\n=== OCR FULL ===")
        print(text_full)

        doc_type = detect_document_type(text_full)
        print(f"\n=== DOCUMENT TYPE === {doc_type}")

        tahun = extract_year(text_full)

        ai_result = extract_with_qwen(text_structured or text_full)
        print(f"\n=== QWEN RESULT === {ai_result}")

        nama_ai, tahun_ai = parse_qwen_result(ai_result)

        if not tahun and tahun_ai:
            tahun = tahun_ai

        if is_valid_name(nama_ai) and len(nama_ai.split()) >= 2:
            return (nama_ai.strip().title(), tahun, text_full)

        nama_marker = extract_name_between_markers(text_full)
        if is_valid_name(nama_marker) and len(nama_marker.split()) >= 2:
            return (nama_marker.strip().title(), tahun, text_full)

        if nama_ai and len(nama_ai.strip()) >= 3:
            return (nama_ai.strip().title(), tahun, text_full)

        if nama_marker and len(nama_marker.strip()) >= 3:
            return (nama_marker.strip().title(), tahun, text_full)

        return ("Perlu Verifikasi Manual", tahun, text_full)

    except Exception as e:
        print("EXTRACT DATA ERROR:", e)
        return ("Tidak Terdeteksi", None, "")
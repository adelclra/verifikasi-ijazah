import cv2
import pytesseract
import re
import os
import json
from .pdf_utils import pdf_to_images
from .qwen_api import extract_with_qwen   

# =========================
# CONFIG
# =========================
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
os.environ["TESSDATA_PREFIX"] = r"C:\Program Files\Tesseract-OCR\tessdata"


# =========================
# DEBUG SAVE
# =========================
def debug_save_image(img, name):
    os.makedirs("debug", exist_ok=True)
    cv2.imwrite(f"debug/{name}.jpg", img)


# =========================
# PREPROCESS
# =========================
def preprocess(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 15, 7, 21)
    gray = cv2.convertScaleAbs(gray, alpha=1.3, beta=10)
    return gray


# =========================
# ROTATE
# =========================
def rotate_image(img, angle):
    if angle == 0:
        return img
    elif angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)


# =========================
# CLEAN TEXT
# =========================
def clean(text):
    text = re.sub(r"[^A-Za-z0-9\s/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# =========================
# SCORING TEXT
# =========================
def score_text(text):
    text = text.upper()
    score = 0

    keywords = ["IJAZAH", "TAHUN", "SEKOLAH", "MENENGAH"]

    for k in keywords:
        if k in text:
            score += 5

    if re.search(r"20\d{2}", text):
        score += 10

    score += len(text) // 50

    return score


# =========================
# SMART ROTATION + OCR
# =========================
def smart_rotate_and_ocr(img):
    best_text = ""
    best_score = -1
    best_img = img

    for angle in [0, 90, 180, 270]:
        rotated = rotate_image(img, angle)
        processed = preprocess(rotated)

        text = pytesseract.image_to_string(
            processed,
            lang="ind+eng",
            config="--oem 3 --psm 6"
        )

        cleaned = clean(text)
        score = score_text(cleaned)

        print(f"\n=== ROTATION {angle}° SCORE: {score} ===")

        if score > best_score:
            best_score = score
            best_text = cleaned
            best_img = rotated

    debug_save_image(best_img, "0_best_rotation")

    return best_img, best_text


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
# EKSTRAK TAHUN
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
# CLEAN NAMA
# =========================
def clean_name(name):
    if not name:
        return None

    name = re.sub(r"[^A-Za-z\s]", "", name)
    words = name.split()
    words = [w for w in words if len(w) >= 3]

    return " ".join(words[:4]).title()


# =========================
# VALIDASI NAMA
# =========================
def is_valid_name(name):
    if not name:
        return False

    words = name.split()

    if len(words) < 2:
        return False

    for w in words:
        if len(w) < 3:
            return False

    return True


# =========================
# FALLBACK EKSTRAK NAMA ANTARA MARKER
# =========================
def extract_name_between_markers(text):
    text = text.upper().replace("\n", " ")

    match = re.search(
        r"nama\s+([A-Z\s]{5,})\s+tempat",
        text,
        re.IGNORECASE
    )

    if match:
        candidate = match.group(1)

        candidate = re.sub(r"[^A-Z\s]", "", candidate)
        words = candidate.split()
        words = [w for w in words if len(w) >= 3]

        if len(words) >= 2:
            return " ".join(words[:4]).title()

    return None


# =========================
# PARSE QWEN RESULT
# =========================
def parse_qwen_result(ai_result):
    if not ai_result:
        return None, None

    try:
        data = json.loads(ai_result)
        return data.get("nama"), data.get("tahun")
    except:
        return ai_result.strip(), None


# =========================
# MAIN FUNCTION
# =========================
def extract_data(file_path):
    img = None

    if file_path.lower().endswith(".pdf"):
        images = pdf_to_images(file_path)
        if images:
            img = cv2.imread(images[0])
    else:
        img = cv2.imread(file_path)

    if img is None:
        return "Gagal OCR", None, ""

    img = cv2.resize(img, None, fx=1.8, fy=1.8)

    img, text_full = smart_rotate_and_ocr(img)

    print("\n=== OCR FULL ===\n", text_full)

    doc_type = detect_document_type(text_full)
    print("\n=== DOCUMENT TYPE ===\n", doc_type)

    # =========================
    # AI (QWEN)
    # =========================
    ai_result = extract_with_qwen(text_full)

    print("\n=== QWEN RESULT ===\n", ai_result)

    nama_ai, _ = parse_qwen_result(ai_result)

    if is_valid_name(nama_ai):
        return clean_name(nama_ai), extract_year(text_full), text_full

    # =========================
    # FALLBACK 
    # =========================
    nama_marker = extract_name_between_markers(text_full)

    if is_valid_name(nama_marker):
        return nama_marker, extract_year(text_full), text_full

    return "Perlu Verifikasi Manual", extract_year(text_full), text_full
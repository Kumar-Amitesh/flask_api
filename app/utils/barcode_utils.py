import cv2
import numpy as np
from pyzbar.pyzbar import decode
import pytesseract
import re

# -----------------------------
# Checksum validation functions
# -----------------------------
def validate_ean13(code):
    if len(code) != 13 or not code.isdigit():
        return False
    digits = list(map(int, code))
    checksum = (10 - (sum(digits[-2::-2]) * 3 + sum(digits[-3::-2])) % 10) % 10
    return checksum == digits[-1]

def validate_upca(code):
    if len(code) != 12 or not code.isdigit():
        return False
    digits = list(map(int, code))
    checksum = (10 - (sum(digits[-2::-2]) * 3 + sum(digits[-3::-2])) % 10) % 10
    return checksum == digits[-1]

# -----------------------------
# OCR digit extractor
# -----------------------------
def extract_digits_ocr(image):
    config = "--psm 6 -c tessedit_char_whitelist=0123456789"
    text = pytesseract.image_to_string(image, config=config)
    digits = re.findall(r"\d+", text)
    return digits

# -----------------------------
# Preprocessing variants
# -----------------------------
def preprocess_variants(image):
    variants = []

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    variants.append(gray)

    # CLAHE for faded images
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    variants.append(clahe.apply(gray))

    # Gaussian blur + adaptive threshold
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh1 = cv2.adaptiveThreshold(
        blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 11, 2
    )
    variants.append(thresh1)

    # Otsu threshold
    _, thresh2 = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    variants.append(thresh2)

    # Morphology (helps broken bars)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    morph = cv2.morphologyEx(thresh2, cv2.MORPH_CLOSE, kernel)
    variants.append(morph)

    return variants

# -----------------------------
# MAIN BARCODE READER
# -----------------------------
def read_barcode_production(image):
    result = {
        "barcode": None,
        "type": None,
        "source": None,
        "error": None
    }

    # Step 1: Try decoding on full image + variants
    for variant in preprocess_variants(image):
        barcodes = decode(variant)
        if barcodes:
            b = barcodes[0]
            result["barcode"] = b.data.decode("utf-8")
            result["type"] = b.type
            result["source"] = "barcode"
            return result

    # Step 2: OCR fallback
    digits_found = extract_digits_ocr(image)

    for d in digits_found:
        if len(d) == 13 and validate_ean13(d):
            result["barcode"] = d
            result["type"] = "EAN13"
            result["source"] = "OCR"
            return result
        if len(d) == 12 and validate_upca(d):
            result["barcode"] = d
            result["type"] = "UPCA"
            result["source"] = "OCR"
            return result

    # Step 3: Failure
    result["error"] = "UNREADABLE_BARCODE"
    return result

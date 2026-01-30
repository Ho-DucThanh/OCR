from __future__ import annotations

from pathlib import Path

import cv2
import pytesseract

from ..config import get_settings


def preprocess_for_ocr(image_path: str) -> "cv2.Mat":
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, d=7, sigmaColor=75, sigmaSpace=75)

    thr = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        9,
    )

    return thr


def run_tesseract(image_path: str, lang: str = "vie") -> str:
    settings = get_settings()
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    processed = preprocess_for_ocr(image_path)

    config = "--oem 3 --psm 6"
    text = pytesseract.image_to_string(processed, lang=lang, config=config)
    return text.strip()


def ensure_upload_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

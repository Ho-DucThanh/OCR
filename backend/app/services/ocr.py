from __future__ import annotations

import os
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


def _guess_tessdata_dir(settings) -> Path | None:
    # Highest priority: explicit env/config
    if settings.tessdata_prefix:
        p = Path(settings.tessdata_prefix)
        return p if p.exists() else None

    # Next: based on TESSERACT_CMD
    if settings.tesseract_cmd:
        p = Path(settings.tesseract_cmd).parent / "tessdata"
        if p.exists():
            return p

    # Common Windows install locations
    if os.name == "nt":
        candidates = [
            Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tessdata"),
        ]
        for c in candidates:
            if c.exists():
                return c

    return None


def _list_installed_langs(tessdata_dir: Path) -> set[str]:
    try:
        return {p.stem for p in tessdata_dir.glob("*.traineddata") if p.is_file()}
    except Exception:
        return set()


def run_tesseract(image_path: str, lang: str | None = None) -> str:
    settings = get_settings()
    if settings.tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    # If user doesn't provide TESSDATA_PREFIX, try to infer it.
    tessdata_dir = _guess_tessdata_dir(settings)
    if tessdata_dir is not None:
        os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)

    processed = preprocess_for_ocr(image_path)

    config = "--oem 3 --psm 6"
    primary_lang = (lang or "").strip() or settings.ocr_lang

    # If we can see installed languages and primary is missing, try fallback early.
    installed = _list_installed_langs(tessdata_dir) if tessdata_dir is not None else set()
    fallback_lang = (settings.ocr_fallback_lang or "").strip() or None
    if installed and primary_lang not in installed and fallback_lang and fallback_lang in installed:
        primary_lang = fallback_lang

    try:
        text = pytesseract.image_to_string(processed, lang=primary_lang, config=config)
        return text.strip()
    except Exception as e:
        # If language pack is missing, optionally fall back to a secondary language.
        if fallback_lang and fallback_lang != primary_lang:
            try:
                text = pytesseract.image_to_string(processed, lang=fallback_lang, config=config)
                return text.strip()
            except Exception:
                pass

        if installed:
            raise RuntimeError(
                f"Tesseract OCR failed for lang='{primary_lang}'. Installed languages: {sorted(installed)}. Details: {e}"
            )
        raise


def ensure_upload_dir(path: str) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p

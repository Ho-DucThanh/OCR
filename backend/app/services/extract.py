from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedFields:
    store_name: str | None
    date: str | None
    total_amount: float | None


_DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"),
    re.compile(r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})\b"),
]

_TOTAL_KEYWORDS = [
    "tong", "tổng", "total", "thanh toan", "thành toán", "pay", "amount",
]


def _normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[\t\r]+", " ", text)
    return text


def extract_store_name(text: str) -> str | None:
    lines = [ln.strip() for ln in _normalize_text(text).split("\n") if ln.strip()]
    if not lines:
        return None

    for ln in lines[:8]:
        cleaned = re.sub(r"[^0-9A-Za-zÀ-ỹ&.()\- ]+", " ", ln)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        if len(cleaned) >= 3 and not re.search(r"\b(hoa don|hóa đơn|invoice|receipt)\b", cleaned, re.I):
            return cleaned
    return lines[0][:255]


def extract_date(text: str) -> str | None:
    normalized = _normalize_text(text)
    for pattern in _DATE_PATTERNS:
        m = pattern.search(normalized)
        if m:
            return m.group(1)
    return None


def _parse_money_token(token: str) -> float | None:
    token = token.strip()
    token = token.replace(" ", "")

    if not token:
        return None

    token = token.replace(".", "")

    if token.count(",") == 1 and re.fullmatch(r"\d+,\d{1,2}", token):
        token = token.replace(",", ".")
    else:
        token = token.replace(",", "")

    try:
        value = float(token)
    except ValueError:
        return None

    if value <= 0:
        return None
    return value


def extract_total_amount(text: str) -> float | None:
    normalized = _normalize_text(text)
    lines = [ln.strip() for ln in normalized.split("\n") if ln.strip()]

    for ln in lines:
        ln_lower = ln.lower()
        if any(k in ln_lower for k in _TOTAL_KEYWORDS):
            tokens = re.findall(r"\d[\d., ]{2,}", ln)
            parsed = [v for v in (_parse_money_token(t) for t in tokens) if v is not None]
            if parsed:
                return max(parsed)

    tokens = re.findall(r"\d[\d., ]{2,}", normalized)
    parsed = [v for v in (_parse_money_token(t) for t in tokens) if v is not None]
    if not parsed:
        return None
    return max(parsed)


def extract_fields(text: str) -> ExtractedFields:
    return ExtractedFields(
        store_name=extract_store_name(text),
        date=extract_date(text),
        total_amount=extract_total_amount(text),
    )

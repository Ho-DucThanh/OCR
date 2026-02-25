from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedFields:
    store_name: str | None
    date: str | None
    total_amount: float | None


@dataclass(frozen=True)
class ExtractedLineItem:
    item_name: str | None
    quantity: float | None
    unit_price: float | None
    total_price: float | None


_DATE_PATTERNS = [
    # Prefer 4-digit year to avoid matching phone numbers like 84-28-3910
    re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{4})(?:\s+\d{1,2}:\d{2})?\b"),
    re.compile(r"\b(\d{4}[/-]\d{1,2}[/-]\d{1,2})(?:\s+\d{1,2}:\d{2})?\b"),
]

_DATE_LABELED_RE = re.compile(
    r"\b(date|ngay|ngày)\b\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})(?:\s+(\d{1,2}:\d{2}))?",
    re.I,
)

_TOTAL_KEYWORDS = [
    "tong", "tổng", "total", "thanh toan", "thành toán", "pay", "amount",
]

_STORE_STOPWORDS_RE = re.compile(
    r"\b(hoa\s*don|hóa\s*đơn|invoice|receipt|sales|date|cashier|payment|paid|subtotal|sub\s*total|tax|total)\b",
    re.I,
)

_ADDRESS_HINT_RE = re.compile(
    r"\b(st\.?|street|dist\.?|district|ward|city|tel|phone|phu\s*nhuan|ho\s*chi\s*minh|vn\d+)\b",
    re.I,
)


def clean_ocr_text(text: str) -> str:
    """Normalize OCR output for downstream extraction/display.

    - Removes decorative separator lines (----, =====, etc.)
    - Strips characters that are almost always OCR noise for receipts
    - Collapses whitespace
    """

    text = _normalize_text(text)

    cleaned_lines: list[str] = []
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line:
            continue

        # Drop separator lines like "-----" or "====="
        if re.fullmatch(r"[\-_=*~.]{3,}", line):
            continue

        # Keep letters/digits (incl. Vietnamese), spaces, and a small set of punctuation.
        line = re.sub(r"[^0-9A-Za-zÀ-ỹ&()\-.,:/+%#' ]+", " ", line)
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue

        # Drop very low-signal lines (common OCR garbage like "TT Se ee EL")
        alnum = sum(1 for ch in line if ch.isalnum())
        letters = sum(1 for ch in line if ch.isalpha())
        if len(line) >= 6:
            ratio = alnum / max(len(line), 1)
            tokens = line.split()
            has_long_token = any(len(t) >= 4 for t in tokens)
            short_token_ratio = (
                sum(1 for t in tokens if len(t) <= 2) / max(len(tokens), 1)
            )
            if (letters < 3 and ratio < 0.5) or (not has_long_token and short_token_ratio > 0.7):
                continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)


def _normalize_text(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[\t\r]+", " ", text)
    return text


def extract_store_name(text: str) -> str | None:
    text = clean_ocr_text(text)
    lines = [ln.strip() for ln in text.split("\n") if ln.strip()]
    if not lines:
        return None

    # Business rule (per app UX): store name is always the first line on the receipt.
    # We intentionally ignore address/phone lines that usually follow.
    return lines[0][:255]


def extract_date(text: str) -> str | None:
    normalized = clean_ocr_text(text)

    # Prefer explicit labeled date (e.g. "Date: 02/09/2026 14:45" or "Ngày: ...").
    for ln in (s.strip() for s in normalized.split("\n")):
        if not ln:
            continue
        m = _DATE_LABELED_RE.search(ln)
        if m:
            d = m.group(2)
            t = m.group(3)
            return f"{d} {t}".strip() if t else d

    for pattern in _DATE_PATTERNS:
        m = pattern.search(normalized)
        if m:
            return m.group(1)
    return None


def _parse_quantity_token(token: str) -> float | None:
    token = token.strip()
    if not token:
        return None
    # Reject tokens that look like money (contain separators like ',' '.' in a long digit group)
    # but accept simple integer/float quantities.
    if re.search(r"[A-Za-z]", token):
        return None
    token = token.replace(",", ".")
    try:
        v = float(token)
    except ValueError:
        return None
    if v <= 0:
        return None
    if v > 10_000:
        return None
    return v


_ITEM_STOP_RE = re.compile(
    r"\b(sub\s*total|subtotal|tax|vat|total|tong|tổng|payment|paid|change|cashier)\b",
    re.I,
)


def extract_line_items(text: str) -> list[ExtractedLineItem]:
    """Extract line items from OCR text using lightweight heuristics.

    Supports common receipt layouts like:
      ITEM  QTY  PRICE  TOTAL
      T-SHIRT ... 1 250,000 250,000
    """

    normalized = clean_ocr_text(text)
    lines = [ln.strip() for ln in normalized.split("\n") if ln.strip()]
    if not lines:
        return []

    header_idx: int | None = None
    header_re = re.compile(r"\b(item|tên)\b.*\b(qty|sl|s\.?l\.?|quantity)\b", re.I)
    for i, ln in enumerate(lines[:80]):
        if header_re.search(ln):
            header_idx = i
            break

    start = (header_idx + 1) if header_idx is not None else 0
    candidates = lines[start:]

    extracted: list[ExtractedLineItem] = []

    # Most receipts have items before SUBTOTAL/TOTAL blocks.
    for ln in candidates:
        if _ITEM_STOP_RE.search(ln):
            if extracted:
                break
            continue

        # Skip obvious non-item lines.
        if _STORE_STOPWORDS_RE.search(ln):
            continue
        if ln.lower() in {"item", "items", "qty", "price", "total"}:
            continue

        # Try strict pattern first: name + qty + unit + total (numbers at line end)
        m = re.match(
            r"^(?P<name>.+?)\s+(?P<qty>\d+(?:[\.,]\d+)?)\s+(?P<unit>[\d., ]{2,})\s+(?P<tot>[\d., ]{2,})(?:\s*(?:vnd|đ|d))?$",
            ln,
            flags=re.I,
        )
        if m:
            name = m.group("name").strip()[:255]
            qty = _parse_quantity_token(m.group("qty"))
            unit = _parse_money_token(m.group("unit"))
            tot = _parse_money_token(m.group("tot"))
            if tot is None or (name and len(name) < 2):
                continue
            if qty is None:
                qty = 1.0
            if unit is None and tot is not None and qty:
                unit = tot / qty
            extracted.append(
                ExtractedLineItem(
                    item_name=name or None,
                    quantity=qty,
                    unit_price=unit,
                    total_price=tot,
                )
            )
            continue

        # Heuristic fallback: parse from right-most numeric tokens.
        tokens = ln.split()
        if len(tokens) < 3:
            continue

        # Strip common currency suffixes on last token.
        stripped_tokens: list[str] = []
        for t in tokens:
            stripped_tokens.append(re.sub(r"(?i)(vnd|đ)$", "", t))
        tokens = stripped_tokens

        total_price = _parse_money_token(tokens[-1])
        unit_price = _parse_money_token(tokens[-2])
        quantity = _parse_quantity_token(tokens[-3]) if len(tokens) >= 3 else None
        name_tokens = tokens[:-3]
        if total_price is None:
            continue

        # Sometimes OCR misses unit price; allow "name qty total".
        if unit_price is None and len(tokens) >= 2:
            unit_price = _parse_money_token(tokens[-1])

        if quantity is None:
            # Try "name qty unit total" where qty is 4th from end.
            if len(tokens) >= 4:
                quantity = _parse_quantity_token(tokens[-4])
                if quantity is not None:
                    name_tokens = tokens[:-4]
                    unit_price = _parse_money_token(tokens[-3])
                    total_price = _parse_money_token(tokens[-1])

        if quantity is None:
            quantity = 1.0

        item_name = " ".join(name_tokens).strip()
        if not item_name or sum(1 for c in item_name if c.isalpha()) < 2:
            continue

        if unit_price is None and total_price is not None and quantity:
            unit_price = total_price / quantity

        extracted.append(
            ExtractedLineItem(
                item_name=item_name[:255],
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
            )
        )

    # De-dup identical consecutive lines (common OCR artifact)
    deduped: list[ExtractedLineItem] = []
    for it in extracted:
        if not deduped:
            deduped.append(it)
            continue
        prev = deduped[-1]
        if (
            (prev.item_name or "").strip().lower() == (it.item_name or "").strip().lower()
            and (prev.quantity == it.quantity)
            and (prev.total_price == it.total_price)
        ):
            continue
        deduped.append(it)

    return deduped


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
    normalized = clean_ocr_text(text)
    lines = [ln.strip() for ln in normalized.split("\n") if ln.strip()]

    total_word_re = re.compile(r"\b(total|tổng|thành\s*toán|amount)\b", re.I)
    subtotal_re = re.compile(r"\b(sub\s*total|subtotal)\b", re.I)
    tax_re = re.compile(r"\b(tax|vat)\b", re.I)

    # Pass 1: prefer explicit TOTAL lines, exclude SUBTOTAL/TAX.
    best: float | None = None
    for ln in lines:
        if not total_word_re.search(ln):
            continue
        if subtotal_re.search(ln) or tax_re.search(ln):
            continue
        tokens = re.findall(r"\d[\d., ]{2,}", ln)
        parsed = [v for v in (_parse_money_token(t) for t in tokens) if v is not None]
        if parsed:
            cand = max(parsed)
            best = cand if best is None else max(best, cand)

    if best is not None:
        return best

    # Pass 2: fallback to keyword-based scan (including subtotal etc.)
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
    text = clean_ocr_text(text)
    return ExtractedFields(
        store_name=extract_store_name(text),
        date=extract_date(text),
        total_amount=extract_total_amount(text),
    )

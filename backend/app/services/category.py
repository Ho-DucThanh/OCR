from __future__ import annotations


RULES: list[tuple[str, str]] = [
    ("circle k", "Ăn uống"),
    ("highlands", "Ăn uống"),
    ("starbucks", "Ăn uống"),
    ("phuc long", "Ăn uống"),
    ("co.op", "Siêu thị"),
    ("coop", "Siêu thị"),
    ("winmart", "Siêu thị"),
    ("lotte", "Siêu thị"),
    ("bach hoa xanh", "Siêu thị"),
    ("shopee", "Mua sắm"),
    ("lazada", "Mua sắm"),
    ("tiki", "Mua sắm"),
    ("grab", "Di chuyển"),
    ("be", "Di chuyển"),
]


def categorize(store_name: str | None) -> str:
    if not store_name:
        return "Khác"

    normalized = store_name.strip().lower()
    for needle, category in RULES:
        if needle in normalized:
            return category
    return "Khác"

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Receipt, ReceiptItem

router = APIRouter(prefix="/api/stats", tags=["stats"])


def _group_from_receipt_category(category: str | None) -> str:
    c = (category or "").strip().lower()
    if not c:
        return "Khác"

    # Heuristic for demo: treat food/drink as "Ăn uống", everything else as "Mua sắm".
    if any(k in c for k in ["ăn", "uống", "cafe", "coffee", "trà", "tea", "nhà hàng", "quán", "food"]):
        return "Ăn uống"

    return "Mua sắm"


@router.get("/spending-by-item")
def spending_by_item(db: Session = Depends(get_db)):
    rows = (
        db.execute(
            select(
                ReceiptItem.item_name,
                func.coalesce(func.sum(ReceiptItem.total_price), 0.0).label("total_spent"),
            )
            .group_by(ReceiptItem.item_name)
            .order_by(func.coalesce(func.sum(ReceiptItem.total_price), 0.0).desc())
        )
        .all()
    )

    return [
        {
            "item_name": (name or "(Không rõ)"),
            "total_spent": float(total or 0.0),
        }
        for name, total in rows
    ]


@router.get("/category-totals")
def category_totals(db: Session = Depends(get_db)):
    # Sum by receipt category (based on receipt total_amount)
    receipts = db.execute(select(Receipt.category, Receipt.total_amount)).all()

    totals: dict[str, float] = {"Ăn uống": 0.0, "Mua sắm": 0.0, "Khác": 0.0}
    for category, total_amount in receipts:
        group = _group_from_receipt_category(category)
        totals[group] = totals.get(group, 0.0) + float(total_amount or 0.0)

    return {
        "groups": [
            {"group": k, "total": float(v)}
            for k, v in sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
        ]
    }

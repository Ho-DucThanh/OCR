from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReceiptItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    receipt_id: int
    item_name: str | None
    quantity: float | None
    unit_price: float | None
    total_price: float | None


class ReceiptItemCreate(BaseModel):
    item_name: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    total_price: float | None = None


class ReceiptItemsReplaceIn(BaseModel):
    items: list[ReceiptItemCreate]


class ReceiptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    store_name: str | None
    date: str | None
    total_amount: float | None
    category: str | None
    image_path: str
    created_at: datetime


class ReceiptDetailOut(ReceiptOut):
    raw_text: str | None

    # Line items extracted from receipt (manual/demo/AI)
    items: list[ReceiptItemOut] = []

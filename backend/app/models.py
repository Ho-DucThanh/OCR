from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    store_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    total_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    category: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)

    image_path: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    items: Mapped[list["ReceiptItem"]] = relationship(
        back_populates="receipt",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ReceiptItem(Base):
    __tablename__ = "receipt_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    receipt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("receipts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    item_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    quantity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    unit_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    receipt: Mapped[Receipt] = relationship(back_populates="items")

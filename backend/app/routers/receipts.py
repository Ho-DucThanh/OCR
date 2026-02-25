from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import delete, desc, select
from sqlalchemy.orm import Session, selectinload

from ..config import get_settings
from ..db import get_db
from ..models import Receipt, ReceiptItem
from ..schemas import (
    ReceiptDetailOut,
    ReceiptItemCreate,
    ReceiptItemOut,
    ReceiptItemsReplaceIn,
    ReceiptOut,
)
from ..services.category import categorize
from ..services.extract import clean_ocr_text, extract_fields, extract_line_items
from ..services.excel import append_receipt_to_excel
from ..services.ocr import ensure_upload_dir, run_tesseract

router = APIRouter(prefix="/api/receipts", tags=["receipts"])


@router.get("/export")
def export_excel(db: Session = Depends(get_db)):
    export_path = Path("exports/receipts.xlsx")

    # Create/overwrite export file
    from openpyxl import Workbook

    wb = Workbook()

    ws_receipts = wb.active
    ws_receipts.title = "receipts"
    ws_receipts.append(
        [
            "id",
            "store_name",
            "date",
            "total_amount",
            "category",
            "image_path",
            "created_at",
        ]
    )

    ws_items = wb.create_sheet(title="items")
    ws_items.append(
        [
            "receipt_id",
            "item_name",
            "quantity",
            "unit_price",
            "total_price",
            "item_id",
        ]
    )

    receipts = (
        db.execute(
            select(Receipt)
            .options(selectinload(Receipt.items))
            .order_by(desc(Receipt.created_at))
        )
        .scalars()
        .all()
    )

    for r in receipts:
        ws_receipts.append(
            [
                r.id,
                r.store_name,
                r.date,
                r.total_amount,
                r.category,
                r.image_path,
                r.created_at.isoformat() if r.created_at else None,
            ]
        )
        for it in (r.items or []):
            ws_items.append(
                [
                    r.id,
                    it.item_name,
                    it.quantity,
                    it.unit_price,
                    it.total_price,
                    it.id,
                ]
            )

    export_path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(export_path)

    return FileResponse(
        path=str(export_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="receipts.xlsx",
    )


@router.get("", response_model=list[ReceiptOut])
def list_receipts(db: Session = Depends(get_db)):
    receipts = db.execute(select(Receipt).order_by(desc(Receipt.created_at))).scalars().all()
    return receipts


@router.get("/{receipt_id}", response_model=ReceiptDetailOut)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = (
        db.execute(
            select(Receipt)
            .options(selectinload(Receipt.items))
            .where(Receipt.id == receipt_id)
        )
        .scalars()
        .first()
    )
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return receipt


@router.get("/{receipt_id}/items", response_model=list[ReceiptItemOut])
def list_receipt_items(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    items = (
        db.execute(
            select(ReceiptItem)
            .where(ReceiptItem.receipt_id == receipt_id)
            .order_by(ReceiptItem.id.asc())
        )
        .scalars()
        .all()
    )
    return items


@router.post("/{receipt_id}/items", response_model=ReceiptItemOut)
def add_receipt_item(receipt_id: int, payload: ReceiptItemCreate, db: Session = Depends(get_db)):
    receipt = db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    item = ReceiptItem(
        receipt_id=receipt_id,
        item_name=payload.item_name,
        quantity=payload.quantity,
        unit_price=payload.unit_price,
        total_price=payload.total_price,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{receipt_id}/items", response_model=list[ReceiptItemOut])
def replace_receipt_items(receipt_id: int, payload: ReceiptItemsReplaceIn, db: Session = Depends(get_db)):
    receipt = db.get(Receipt, receipt_id)
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    # Replace existing items atomically.
    db.execute(delete(ReceiptItem).where(ReceiptItem.receipt_id == receipt_id))

    created: list[ReceiptItem] = []
    for it in payload.items:
        created.append(
            ReceiptItem(
                receipt_id=receipt_id,
                item_name=it.item_name,
                quantity=it.quantity,
                unit_price=it.unit_price,
                total_price=it.total_price,
            )
        )

    if created:
        db.add_all(created)

    db.commit()

    items = (
        db.execute(
            select(ReceiptItem)
            .where(ReceiptItem.receipt_id == receipt_id)
            .order_by(ReceiptItem.id.asc())
        )
        .scalars()
        .all()
    )
    return items


@router.post("/upload", response_model=ReceiptDetailOut)
async def upload_receipt(file: UploadFile = File(...), db: Session = Depends(get_db)):
    settings = get_settings()
    upload_dir = ensure_upload_dir(settings.upload_dir)

    ext = Path(file.filename or "").suffix.lower()
    if ext not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = upload_dir / filename

    content = await file.read()
    dest_path.write_bytes(content)

    try:
        raw_text = run_tesseract(str(dest_path))
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=(
                "OCR failed. Make sure Tesseract is installed and Vietnamese language pack is available. "
                f"Details: {e}"
            ),
        )

    raw_text = clean_ocr_text(raw_text)

    fields = extract_fields(raw_text)
    category = categorize(fields.store_name)

    image_path = str(dest_path.as_posix())
    if os.name == "nt":
        image_path = image_path.replace("\\", "/")

    receipt = Receipt(
        store_name=fields.store_name,
        date=fields.date,
        total_amount=fields.total_amount,
        category=category,
        image_path=image_path,
        raw_text=raw_text,
    )

    db.add(receipt)
    db.commit()
    db.refresh(receipt)

    # Extract and persist line items (best-effort).
    try:
        extracted_items = extract_line_items(raw_text)
        if extracted_items:
            db.add_all(
                [
                    ReceiptItem(
                        receipt_id=receipt.id,
                        item_name=it.item_name,
                        quantity=it.quantity,
                        unit_price=it.unit_price,
                        total_price=it.total_price,
                    )
                    for it in extracted_items
                ]
            )
            db.commit()
    except Exception:
        # Don't fail upload if item extraction is imperfect.
        pass

    # Return with items preloaded for the detail page.
    receipt = (
        db.execute(
            select(Receipt)
            .options(selectinload(Receipt.items))
            .where(Receipt.id == receipt.id)
        )
        .scalars()
        .first()
    )

    # Best-effort append to Excel (local storage)
    try:
        append_receipt_to_excel(receipt, "exports/receipts.xlsx")
    except Exception:
        pass

    return receipt

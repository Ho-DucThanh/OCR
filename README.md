# OCR Receipts Demo (React + FastAPI + MySQL)

## 1) Run MySQL (local via Docker)

From workspace root:

```powershell
cd D:\WorkSpace\OCR
docker compose up -d
```

- MySQL is exposed on host port `3307` (container `3306`).

## 2) Run backend (FastAPI)

Backend reads env from `.env` (workspace root).

```powershell
cd D:\WorkSpace\OCR\backend
./run.ps1
```

Health check:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8001/health
```

## 3) Run frontend (React + Tailwind)

```powershell
cd D:\WorkSpace\OCR\frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open: http://127.0.0.1:5173/

Frontend proxies:

- `/api/*` -> `http://127.0.0.1:8001`
- `/uploads/*` -> `http://127.0.0.1:8001`

## OCR notes (Tesseract)

- Ensure `tesseract.exe` is installed and available in `PATH`, or set `TESSERACT_CMD` in `.env`.
- For Vietnamese receipts, install Vietnamese language data (`vie`).

## API

- `GET /api/receipts` list receipts
- `GET /api/receipts/{id}` receipt detail
- `GET /api/receipts/{id}/items` list receipt items
- `POST /api/receipts/{id}/items` add receipt item
- `PUT /api/receipts/{id}/items` replace all receipt items
- `POST /api/receipts/upload` upload image + OCR + save
- `GET /api/receipts/export` download `receipts.xlsx`

Stats (demo idea for next features):

- `GET /api/stats/spending-by-item`
- `GET /api/stats/category-totals`

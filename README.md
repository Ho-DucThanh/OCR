# OCR Receipts Demo (React + FastAPI + MySQL)

## Quick start

Run these in 3 separate terminals:

1. MySQL

```powershell
cd D:\WorkSpace\OCR
docker compose up -d
```

2. Backend

```powershell
cd D:\WorkSpace\OCR\backend
./run.ps1
```

3. Frontend

```powershell
cd D:\WorkSpace\OCR\frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open: http://127.0.0.1:5173/

## 1) Run MySQL (local via Docker)

From workspace root:

```powershell
cd D:\WorkSpace\OCR
docker compose up -d
```

- MySQL is exposed on host port `3307` (container `3306`).

## 2) Run backend (FastAPI)

Backend reads env from `.env` (workspace root).

Note: the folder in `UPLOAD_DIR` is auto-created on startup.

If `.venv` doesn't exist yet:

```powershell
cd D:\WorkSpace\OCR
py -3.12 -m venv .venv
```

Recommended (auto-kills port 8001 conflicts, loads `.env`):

```powershell
cd D:\WorkSpace\OCR\backend
./run.ps1
```

If PowerShell blocks running scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Manual (if you prefer):

```powershell
cd D:\WorkSpace\OCR
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
& .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
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

### Demo mode (UI preview without backend)

Frontend can show sample data even if backend/MySQL are off:

- Set `VITE_DEMO_MODE=1` in [frontend/.env](frontend/.env)

Frontend proxies:

- `/api/*` -> `http://127.0.0.1:8001`
- `/uploads/*` -> `http://127.0.0.1:8001`

## OCR notes (Tesseract)

- Ensure `tesseract.exe` is installed and available in `PATH`, or set `TESSERACT_CMD` in `.env`.
- For Vietnamese receipts, install Vietnamese language data (`vie`). If you see error like "Failed loading language 'vie'":
  - Ensure `vie.traineddata` exists under `C:\Program Files\Tesseract-OCR\tessdata\vie.traineddata` (or your install folder)
  - Set `TESSDATA_PREFIX` in `.env` to your tessdata folder, e.g. `C:\Program Files\Tesseract-OCR\tessdata`
  - You can temporarily set `OCR_LANG=eng` in `.env` to verify OCR pipeline works

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

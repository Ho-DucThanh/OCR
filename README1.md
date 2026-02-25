# README1 — Hướng dẫn cài đặt & chạy dự án trên máy khác (FE + BE + DB + Docker + OCR)

Tài liệu này liệt kê **tất cả công cụ/thư viện cần cài** và các bước để chạy dự án **OCR Receipts Demo (React + FastAPI + MySQL)** trên một máy tính mới.

> Mặc định hướng dẫn theo **Windows 10/11** (PowerShell). Nếu bạn dùng macOS/Linux, xem thêm mục “Gợi ý cho macOS/Linux”.

---

## 1) Yêu cầu bắt buộc

### A. Công cụ hệ thống

1. **Git**

- Dùng để clone source.
- Cài: https://git-scm.com/downloads

2. **Docker Desktop** (kèm Docker Compose)

- Dùng để chạy MySQL bằng container.
- Cài: https://www.docker.com/products/docker-desktop/
- Sau khi cài xong: mở Docker Desktop để đảm bảo Docker Engine đang chạy.

3. **Node.js (LTS 18+ hoặc 20+)**

- Dùng để chạy/build frontend.
- Cài: https://nodejs.org/
- Kiểm tra:
  ```powershell
  node -v
  npm -v
  ```

4. **Python 3.12+**

- Dùng để chạy backend FastAPI.
- Cài: https://www.python.org/downloads/
- Khi cài, nhớ tick “Add Python to PATH” (khuyến nghị).
- Kiểm tra:
  ```powershell
  py -V
  ```

5. **Tesseract OCR (Windows)**

- Backend gọi Tesseract để OCR.
- Cài Tesseract (ví dụ UB Mannheim build):
  - https://github.com/UB-Mannheim/tesseract/wiki
- Cài thêm language data tiếng Việt (`vie`).
- Kiểm tra:
  ```powershell
  tesseract --version
  tesseract --list-langs
  ```
  Trong danh sách nên có `vie`.

> Nếu `tesseract` không nhận trong PATH, bạn vẫn chạy được bằng cách cấu hình `TESSERACT_CMD` trong `.env`.

---

## 2) Clone dự án

```powershell
git clone <URL_REPO_CUA_BAN>
cd OCR
```

Cấu trúc thư mục chính:

- `backend/` (FastAPI)
- `frontend/` (React + Vite)
- `docker-compose.yml` (MySQL)

---

## 3) Cấu hình biến môi trường (.env)

Backend đọc cấu hình từ file `.env` ở **thư mục root** của repo.

Tạo file `.env` tại `OCR/.env` (cùng cấp với `docker-compose.yml`). Ví dụ:

```env
# Environment
ENVIRONMENT=dev

# MySQL chạy bằng Docker Compose (port host 3307)
DATABASE_URL=mysql+pymysql://ocr:ocr@127.0.0.1:3307/ocr

# Thư mục lưu ảnh upload (tự tạo nếu chưa có)
UPLOAD_DIR=uploads

# CORS: FE chạy Vite thường là 5173
CORS_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

# OCR
OCR_LANG=vie
OCR_FALLBACK_LANG=eng

# Nếu tesseract.exe không nằm trong PATH, set đường dẫn đầy đủ:
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Nếu thiếu vie.traineddata, có thể set tessdata:
# TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
```

---

## 4) Chạy Database (MySQL) bằng Docker

Tại thư mục root `OCR/`:

```powershell
docker compose up -d
```

Ghi chú:

- MySQL container expose ra host port **3307** (container 3306).
- Nếu muốn kiểm tra container:
  ```powershell
  docker ps
  docker logs ocr-mysql --tail 50
  ```

---

## 5) Chạy Backend (FastAPI)

### Cách A (khuyến nghị): dùng script `backend/run.ps1`

Script này sẽ:

- tạo `.venv` nếu chưa có
- `pip install -r backend/requirements.txt`
- load `.env`
- kill tiến trình đang chiếm port `8001` (nếu có)
- chạy Uvicorn tại `127.0.0.1:8001`

Chạy:

```powershell
cd backend
./run.ps1
```

Nếu bị chặn chạy script PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Cách B: chạy thủ công

Tại thư mục root `OCR/`:

```powershell
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
& .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
```

Health check:

```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8001/health
```

---

## 6) Chạy Frontend (React + Vite)

Tại `OCR/frontend/`:

```powershell
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Mở trình duyệt:

- http://127.0.0.1:5173/

Ghi chú:

- Dev server Vite đã cấu hình proxy:
  - `/api/*` → `http://127.0.0.1:8001`
  - `/uploads/*` → `http://127.0.0.1:8001`

---

## 7) Kiểm tra các chức năng chính

- Upload hóa đơn: FE gọi `POST /api/receipts/upload`.
- Xem danh sách hóa đơn: `GET /api/receipts`.
- Xem chi tiết: `GET /api/receipts/{id}`.
- Xem items: `GET /api/receipts/{id}/items`.
- Xuất Excel: `GET /api/receipts/export` (tải `receipts.xlsx`).

---

## 8) Troubleshooting thường gặp

### A) OCR lỗi “Failed loading language 'vie'”

- Cài language pack tiếng Việt cho Tesseract.
- Kiểm tra `tesseract --list-langs` có `vie`.
- Set `TESSDATA_PREFIX` trỏ tới thư mục `tessdata`.
- Tạm thời có thể set `OCR_LANG=eng` để kiểm tra pipeline.

### B) Backend không connect được MySQL

- Đảm bảo `docker compose up -d` đã chạy.
- Kiểm tra port 3307 có bị app khác chiếm không.
- Kiểm tra `DATABASE_URL` đúng: `mysql+pymysql://ocr:ocr@127.0.0.1:3307/ocr`

### C) Frontend gọi API bị CORS

- Kiểm tra `.env` có `CORS_ORIGINS` chứa đúng origin của FE (vd `http://127.0.0.1:5173`).
- Restart backend sau khi đổi `.env`.

### D) Port bị chiếm

- Backend mặc định `8001`, frontend `5173`, MySQL `3307`.
- `backend/run.ps1` có xử lý giải phóng port 8001.

---

## 9) Gợi ý cho macOS/Linux (tóm tắt)

- Cài Docker + docker compose.
- Cài Python 3.12, Node 18+.
- Cài Tesseract + Vietnamese language pack:
  - Ubuntu: `sudo apt-get install tesseract-ocr tesseract-ocr-vie`
  - macOS (Homebrew): `brew install tesseract` + cài thêm language data (tùy theo cách cài)
- Chạy MySQL: `docker compose up -d`
- Chạy backend (venv):
  ```bash
  python3.12 -m venv .venv
  ./.venv/bin/pip install -r backend/requirements.txt
  ./.venv/bin/uvicorn backend.app.main:app --host 127.0.0.1 --port 8001
  ```
- Chạy frontend:
  ```bash
  cd frontend
  npm ci
  npm run dev -- --host 127.0.0.1 --port 5173
  ```

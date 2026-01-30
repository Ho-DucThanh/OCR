import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiPostForm } from "../api";

export default function UploadPage() {
  const nav = useNavigate();
  const [file, setFile] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const previewUrl = useMemo(() => {
    if (!file) return "";
    return URL.createObjectURL(file);
  }, [file]);

  async function onSubmit(e) {
    e.preventDefault();
    if (!file) return;

    setBusy(true);
    setError("");

    try {
      const form = new FormData();
      form.append("file", file);
      const receipt = await apiPostForm("/api/receipts/upload", form);
      nav(`/receipts/${receipt.id}`);
    } catch (e2) {
      setError(e2?.message || String(e2));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-semibold">Tải ảnh hóa đơn</h1>
        <p className="text-sm text-slate-600">
          Upload ảnh chụp hóa đơn để OCR và trích xuất thông tin.
        </p>
      </div>

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Lỗi: {error}
          <div className="mt-1 text-xs text-red-600">
            Nếu báo lỗi OCR: hãy kiểm tra Tesseract đã cài và có ngôn ngữ `vie`.
          </div>
        </div>
      )}

      <form onSubmit={onSubmit} className="space-y-4">
        <div className="rounded-lg border bg-white p-4">
          <label className="block text-sm font-medium">Chọn ảnh</label>
          <input
            type="file"
            accept="image/*"
            className="mt-2 block w-full text-sm"
            onChange={(e) => setFile(e.target.files?.[0] || null)}
          />
          <p className="mt-2 text-xs text-slate-500">
            Hỗ trợ: JPG, PNG, WEBP, TIFF…
          </p>
        </div>

        {previewUrl && (
          <div className="overflow-hidden rounded-lg border bg-white">
            <div className="border-b px-4 py-2 text-sm font-medium">
              Xem trước
            </div>
            <div className="p-4">
              <img
                src={previewUrl}
                alt="preview"
                className="max-h-[520px] w-auto rounded-md border"
              />
            </div>
          </div>
        )}

        <button
          type="submit"
          disabled={!file || busy}
          className="inline-flex items-center justify-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-50"
        >
          {busy ? "Đang xử lý…" : "Upload & OCR"}
        </button>
      </form>
    </div>
  );
}

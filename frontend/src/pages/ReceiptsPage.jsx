import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { apiGet } from "../api";

function formatMoney(v) {
  if (v === null || v === undefined) return "";
  try {
    return new Intl.NumberFormat("vi-VN").format(v);
  } catch {
    return String(v);
  }
}

export default function ReceiptsPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    apiGet("/api/receipts")
      .then((data) => {
        if (!mounted) return;
        setItems(Array.isArray(data) ? data : []);
        setError("");
      })
      .catch((e) => {
        if (!mounted) return;
        setError(e?.message || String(e));
      })
      .finally(() => {
        if (!mounted) return;
        setLoading(false);
      });

    return () => {
      mounted = false;
    };
  }, []);

  const total = useMemo(() => {
    return items.reduce(
      (sum, r) =>
        sum + (typeof r.total_amount === "number" ? r.total_amount : 0),
      0,
    );
  }, [items]);

  return (
    <div className="space-y-4">
      {/* {String(import.meta.env.VITE_DEMO_MODE || "").toLowerCase() !== "0" &&
        String(import.meta.env.VITE_DEMO_MODE || "").toLowerCase() !==
          "false" && (
          <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
            Đang ở <span className="font-medium">Demo mode</span> (dữ liệu mẫu,
            không cần backend).
          </div>
        )} */}
      <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Bảng chi tiêu</h1>
          <p className="text-sm text-slate-600">
            Tổng chi:{" "}
            <span className="font-medium">{formatMoney(total)} VND</span>
          </p>
        </div>
        <div className="flex gap-2">
          <Link
            to="/stats"
            className="inline-flex items-center justify-center rounded-md border bg-white px-4 py-2 text-sm font-medium text-slate-900 hover:bg-slate-50"
          >
            Xem thống kê
          </Link>
          <Link
            to="/upload"
            className="inline-flex items-center justify-center rounded-md bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
          >
            + Tải hóa đơn
          </Link>
        </div>
      </div>

      {loading && (
        <div className="text-sm text-slate-600">Đang tải dữ liệu…</div>
      )}
      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Lỗi: {error}
          <div className="mt-1 text-xs text-red-600">
            Gợi ý: đảm bảo backend đang chạy và MySQL đang bật.
          </div>
        </div>
      )}

      {!loading && !error && (
        <div className="overflow-hidden rounded-lg border bg-white">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-600">
              <tr>
                <th className="px-4 py-3">Cửa hàng</th>
                <th className="px-4 py-3">Ngày</th>
                <th className="px-4 py-3">Tổng tiền</th>
                <th className="px-4 py-3">Loại chi tiêu</th>
                <th className="px-4 py-3 ">Chi tiết</th>
              </tr>
            </thead>
            <tbody>
              {items.map((r) => (
                <tr key={r.id} className="border-t">
                  <td className="px-4 py-3 font-medium">
                    {r.store_name || "-"}
                  </td>
                  <td className="px-4 py-3">{r.date || "-"}</td>
                  <td className="px-4 py-3">
                    {formatMoney(r.total_amount) || "-"}
                  </td>
                  <td className="px-4 py-3">{r.category || "-"}</td>
                  <td className="px-4 py-3 ">
                    <Link
                      to={`/receipts/${r.id}`}
                      className="rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
                    >
                      Xem
                    </Link>
                  </td>
                </tr>
              ))}
              {items.length === 0 && (
                <tr>
                  <td
                    className="px-4 py-6 text-center text-slate-500"
                    colSpan={5}
                  >
                    Chưa có dữ liệu. Hãy tải hóa đơn đầu tiên.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* <div className="text-xs text-slate-500">
        Lưu ý: OCR có thể sai; bạn có thể cải thiện bằng ảnh rõ nét và đủ sáng.
      </div> */}
    </div>
  );
}

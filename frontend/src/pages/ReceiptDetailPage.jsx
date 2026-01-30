import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { apiGet } from "../api";

function formatMoney(v) {
  if (v === null || v === undefined) return "";
  try {
    return new Intl.NumberFormat("vi-VN").format(v);
  } catch {
    return String(v);
  }
}

export default function ReceiptDetailPage() {
  const { id } = useParams();
  const [item, setItem] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    Promise.all([
      apiGet(`/api/receipts/${id}`),
      apiGet(`/api/receipts/${id}/items`),
    ])
      .then(([data, lineItems]) => {
        if (!mounted) return;
        setItem(data);
        setItems(
          Array.isArray(lineItems)
            ? lineItems
            : Array.isArray(data?.items)
              ? data.items
              : [],
        );
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
  }, [id]);

  if (loading) return <div className="text-sm text-slate-600">Đang tải…</div>;

  if (error) {
    return (
      <div className="space-y-3">
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Lỗi: {error}
        </div>
        <Link to="/" className="text-sm text-slate-700 underline">
          ← Quay lại
        </Link>
      </div>
    );
  }

  if (!item) return null;

  const itemsTotal = items.reduce(
    (sum, it) =>
      sum +
      (typeof it.total_price === "number"
        ? it.total_price
        : Number(it.total_price) || 0),
    0,
  );

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Chi tiết hóa đơn</h1>
          <p className="text-sm text-slate-600">ID: {item.id}</p>
        </div>
        <Link
          to="/"
          className="rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
        >
          ← Bảng chi tiêu
        </Link>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="overflow-hidden rounded-lg border bg-white">
          <div className="border-b px-4 py-2 text-sm font-medium">
            Ảnh hóa đơn
          </div>
          <div className="p-4">
            <img
              src={
                item.image_path.startsWith("http")
                  ? item.image_path
                  : `/${item.image_path.replace(/^\/+/, "")}`
              }
              alt="receipt"
              className="max-h-[720px] w-auto rounded-md border"
            />
          </div>
        </div>

        <div className="space-y-4">
          <div className="rounded-lg border bg-white p-4">
            <div className="grid grid-cols-3 gap-3 text-sm">
              <div className="text-slate-500">Cửa hàng</div>
              <div className="col-span-2 font-medium">
                {item.store_name || "-"}
              </div>

              <div className="text-slate-500">Ngày</div>
              <div className="col-span-2">{item.date || "-"}</div>

              <div className="text-slate-500">Tổng tiền</div>
              <div className="col-span-2">
                {formatMoney(item.total_amount) || "-"} VND
              </div>

              <div className="text-slate-500">Loại</div>
              <div className="col-span-2">{item.category || "-"}</div>
            </div>
          </div>

          <div className="overflow-hidden rounded-lg border bg-white">
            <div className="flex items-center justify-between border-b px-4 py-2">
              <div className="text-sm font-medium">Mặt hàng</div>
              <div className="text-xs text-slate-500">
                Tổng theo items: {formatMoney(itemsTotal)} VND
              </div>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-50 text-xs uppercase text-slate-600">
                  <tr>
                    <th className="px-4 py-3">Tên</th>
                    <th className="px-4 py-3">SL</th>
                    <th className="px-4 py-3">Đơn giá</th>
                    <th className="px-4 py-3">Thành tiền</th>
                  </tr>
                </thead>
                <tbody>
                  {items.map((it) => (
                    <tr key={it.id} className="border-t">
                      <td className="px-4 py-3 font-medium">
                        {it.item_name || "-"}
                      </td>
                      <td className="px-4 py-3">{it.quantity ?? "-"}</td>
                      <td className="px-4 py-3">
                        {formatMoney(it.unit_price) || "-"}
                      </td>
                      <td className="px-4 py-3">
                        {formatMoney(it.total_price) || "-"}
                      </td>
                    </tr>
                  ))}
                  {items.length === 0 && (
                    <tr>
                      <td
                        className="px-4 py-6 text-center text-slate-500"
                        colSpan={4}
                      >
                        Chưa có dữ liệu mặt hàng (demo/AI sẽ bổ sung sau).
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            {typeof item.total_amount === "number" && items.length > 0 && (
              <div className="border-t px-4 py-3 text-xs text-slate-600">
                Chênh lệch so với tổng hóa đơn:{" "}
                {formatMoney(item.total_amount - itemsTotal)} VND
              </div>
            )}
          </div>

          <div className="overflow-hidden rounded-lg border bg-white">
            <div className="border-b px-4 py-2 text-sm font-medium">
              Raw OCR Text
            </div>
            <pre className="max-h-[360px] overflow-auto whitespace-pre-wrap p-4 text-xs text-slate-700">
              {item.raw_text || ""}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}

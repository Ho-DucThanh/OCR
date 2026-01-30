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

function clamp01(x) {
  const n = Number(x) || 0;
  if (n < 0) return 0;
  if (n > 1) return 1;
  return n;
}

export default function StatsPage() {
  const [byItem, setByItem] = useState([]);
  const [byGroup, setByGroup] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;
    setLoading(true);
    setError("");

    Promise.all([
      apiGet("/api/stats/spending-by-item"),
      apiGet("/api/stats/category-totals"),
    ])
      .then(([items, groups]) => {
        if (!mounted) return;
        setByItem(Array.isArray(items) ? items : []);
        setByGroup(Array.isArray(groups?.groups) ? groups.groups : []);
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

  const totalGroupSpend = useMemo(() => {
    return byGroup.reduce((s, g) => s + (Number(g.total) || 0), 0);
  }, [byGroup]);

  const topItemTotal = useMemo(() => {
    return Math.max(0, ...byItem.map((x) => Number(x.total_spent) || 0));
  }, [byItem]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold">Thống kê</h1>
          <p className="text-sm text-slate-600">
            Demo ý tưởng: chi tiêu theo mặt hàng và theo nhóm chi tiêu.
          </p>
        </div>
        <Link
          to="/"
          className="rounded-md px-3 py-2 text-sm text-slate-700 hover:bg-slate-100"
        >
          ← Bảng chi tiêu
        </Link>
      </div>

      {loading && <div className="text-sm text-slate-600">Đang tải…</div>}

      {error && (
        <div className="rounded-md border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          Lỗi: {error}
        </div>
      )}

      {!loading && !error && (
        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-lg border bg-white p-4">
            <div className="mb-3 flex items-baseline justify-between">
              <div className="text-sm font-medium">
                Tổng tiền ăn uống / mua sắm
              </div>
              <div className="text-xs text-slate-500">
                Tổng: {formatMoney(totalGroupSpend)} VND
              </div>
            </div>

            <div className="space-y-3">
              {byGroup.map((g) => {
                const ratio = totalGroupSpend
                  ? clamp01((Number(g.total) || 0) / totalGroupSpend)
                  : 0;
                return (
                  <div key={g.group} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <div className="font-medium">{g.group}</div>
                      <div className="text-slate-700">
                        {formatMoney(g.total)} VND
                      </div>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-slate-100">
                      <div
                        className="h-full rounded-full bg-slate-900"
                        style={{ width: `${Math.round(ratio * 100)}%` }}
                      />
                    </div>
                  </div>
                );
              })}
              {byGroup.length === 0 && (
                <div className="text-sm text-slate-500">Chưa có dữ liệu.</div>
              )}
            </div>
          </div>

          <div className="overflow-hidden rounded-lg border bg-white">
            <div className="border-b px-4 py-3 text-sm font-medium">
              Chi tiêu theo mặt hàng (top)
            </div>
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-xs uppercase text-slate-600">
                <tr>
                  <th className="px-4 py-3">Mặt hàng</th>
                  <th className="px-4 py-3">Tổng chi</th>
                </tr>
              </thead>
              <tbody>
                {byItem.slice(0, 12).map((x) => {
                  const ratio = topItemTotal
                    ? clamp01((Number(x.total_spent) || 0) / topItemTotal)
                    : 0;
                  return (
                    <tr key={x.item_name} className="border-t">
                      <td className="px-4 py-3">
                        <div className="font-medium">{x.item_name}</div>
                        <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-100">
                          <div
                            className="h-full rounded-full bg-emerald-600"
                            style={{ width: `${Math.round(ratio * 100)}%` }}
                          />
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        {formatMoney(x.total_spent)}
                      </td>
                    </tr>
                  );
                })}
                {byItem.length === 0 && (
                  <tr>
                    <td
                      className="px-4 py-6 text-center text-slate-500"
                      colSpan={2}
                    >
                      Chưa có dữ liệu.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="text-xs text-slate-500">
        Gợi ý bước tiếp theo: cho phép chỉnh sửa items trong chi tiết hóa đơn,
        rồi lưu về backend để thống kê chính xác hơn.
      </div>
    </div>
  );
}

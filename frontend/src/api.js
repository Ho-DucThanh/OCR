import {
  demoGetReceipt,
  demoCategoryTotals,
  demoListReceipts,
  demoListReceiptItems,
  demoReplaceReceiptItems,
  demoSpendingByItem,
  demoUploadReceipt,
} from "./demoStore";

const defaultHeaders = {
  Accept: "application/json",
};

const DEMO_MODE =
  String(import.meta.env.VITE_DEMO_MODE || "").toLowerCase() === "1" ||
  String(import.meta.env.VITE_DEMO_MODE || "").toLowerCase() === "true";

const API_BASE = import.meta.env.VITE_API_BASE || "";

function withBase(path) {
  if (!API_BASE) return path;
  return `${API_BASE}${path}`;
}

function isReceiptsList(path) {
  return path === "/api/receipts";
}

function isReceiptDetail(path) {
  return /^\/api\/receipts\/(\d+)$/.test(path);
}

function receiptIdFromPath(path) {
  const m = path.match(/^\/api\/receipts\/(\d+)$/);
  return m ? Number(m[1]) : null;
}

function isReceiptItems(path) {
  return /^\/api\/receipts\/(\d+)\/items$/.test(path);
}

function receiptIdFromItemsPath(path) {
  const m = path.match(/^\/api\/receipts\/(\d+)\/items$/);
  return m ? Number(m[1]) : null;
}

function isStatsSpendingByItem(path) {
  return path === "/api/stats/spending-by-item";
}

function isStatsCategoryTotals(path) {
  return path === "/api/stats/category-totals";
}

export async function apiGet(path) {
  if (DEMO_MODE) {
    if (isReceiptsList(path)) return demoListReceipts();
    if (isReceiptDetail(path)) return demoGetReceipt(receiptIdFromPath(path));
    if (isReceiptItems(path))
      return demoListReceiptItems(receiptIdFromItemsPath(path));
    if (isStatsSpendingByItem(path)) return demoSpendingByItem();
    if (isStatsCategoryTotals(path)) return demoCategoryTotals();
    throw new Error("Demo mode: endpoint not supported");
  }

  try {
    const res = await fetch(withBase(path), { headers: defaultHeaders });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (e) {
    // Friendly fallback so you can preview UI without backend.
    if (isReceiptsList(path)) return demoListReceipts();
    if (isReceiptDetail(path)) return demoGetReceipt(receiptIdFromPath(path));
    if (isReceiptItems(path))
      return demoListReceiptItems(receiptIdFromItemsPath(path));
    if (isStatsSpendingByItem(path)) return demoSpendingByItem();
    if (isStatsCategoryTotals(path)) return demoCategoryTotals();
    throw e;
  }
}

export async function apiPutJson(path, payload) {
  if (DEMO_MODE) {
    if (isReceiptItems(path)) {
      const rid = receiptIdFromItemsPath(path);
      return demoReplaceReceiptItems(rid, payload?.items || []);
    }
    throw new Error("Demo mode: endpoint not supported");
  }

  const res = await fetch(withBase(path), {
    method: "PUT",
    headers: { ...defaultHeaders, "Content-Type": "application/json" },
    body: JSON.stringify(payload ?? {}),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return await res.json();
}

export async function apiPostForm(path, formData) {
  if (DEMO_MODE) {
    if (path === "/api/receipts/upload") {
      const f = formData?.get?.("file") || null;
      return demoUploadReceipt(f);
    }
    throw new Error("Demo mode: endpoint not supported");
  }

  const res = await fetch(withBase(path), {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `HTTP ${res.status}`);
  }
  return await res.json();
}

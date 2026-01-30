const STORAGE_KEY = "ocr_demo_receipts_v2";

function nowIso() {
  return new Date().toISOString();
}

function seed() {
  return [
    {
      id: 101,
      store_name: "WinMart",
      date: "25/01/2026",
      total_amount: 63000,
      category: "Siêu thị",
      image_path: "/demo/receipt-1.svg",
      raw_text: "WINMART\n25/01/2026\nTONG THANH TOAN 63,000",
      created_at: nowIso(),
      items: [
        {
          id: 1001,
          receipt_id: 101,
          item_name: "Sữa tươi",
          quantity: 1,
          unit_price: 18000,
          total_price: 18000,
        },
        {
          id: 1002,
          receipt_id: 101,
          item_name: "Mì gói",
          quantity: 3,
          unit_price: 7000,
          total_price: 21000,
        },
        {
          id: 1003,
          receipt_id: 101,
          item_name: "Trứng gà",
          quantity: 1,
          unit_price: 24000,
          total_price: 24000,
        },
      ],
    },
    {
      id: 102,
      store_name: "Highlands Coffee",
      date: "26/01/2026",
      total_amount: 77000,
      category: "Ăn uống",
      image_path: "/demo/receipt-2.svg",
      raw_text: "HIGHLANDS COFFEE\n26/01/2026\nTOTAL 77,000",
      created_at: nowIso(),
      items: [
        {
          id: 2001,
          receipt_id: 102,
          item_name: "Cà phê sữa",
          quantity: 1,
          unit_price: 39000,
          total_price: 39000,
        },
        {
          id: 2002,
          receipt_id: 102,
          item_name: "Bánh ngọt",
          quantity: 1,
          unit_price: 38000,
          total_price: 38000,
        },
      ],
    },
    {
      id: 103,
      store_name: "Circle K",
      date: "20/01/2026",
      total_amount: 60000,
      category: "Ăn uống",
      image_path: "/demo/receipt-3.svg",
      raw_text: "CIRCLE K\n20/01/2026\nTONG 60,000",
      created_at: nowIso(),
      items: [
        {
          id: 3001,
          receipt_id: 103,
          item_name: "Nước suối",
          quantity: 2,
          unit_price: 10000,
          total_price: 20000,
        },
        {
          id: 3002,
          receipt_id: 103,
          item_name: "Snack",
          quantity: 2,
          unit_price: 20000,
          total_price: 40000,
        },
      ],
    },
  ];
}

function groupFromCategory(category) {
  const c = String(category || "")
    .trim()
    .toLowerCase();
  if (!c) return "Khác";
  if (
    [
      "ăn",
      "uống",
      "cafe",
      "coffee",
      "trà",
      "tea",
      "nhà hàng",
      "quán",
      "food",
    ].some((k) => c.includes(k))
  ) {
    return "Ăn uống";
  }
  return "Mua sắm";
}

function loadAll() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return seed();
    const data = JSON.parse(raw);
    if (!Array.isArray(data) || data.length === 0) return seed();
    return data;
  } catch {
    return seed();
  }
}

function saveAll(items) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
}

export function demoListReceipts() {
  const items = loadAll();
  return items
    .slice()
    .sort((a, b) =>
      String(b.created_at || "").localeCompare(String(a.created_at || "")),
    );
}

export function demoGetReceipt(id) {
  const items = loadAll();
  const rid = Number(id);
  return items.find((x) => Number(x.id) === rid) || null;
}

export function demoListReceiptItems(receiptId) {
  const r = demoGetReceipt(receiptId);
  return Array.isArray(r?.items) ? r.items.slice() : [];
}

export function demoReplaceReceiptItems(receiptId, newItems) {
  const all = loadAll();
  const rid = Number(receiptId);
  const idx = all.findIndex((x) => Number(x.id) === rid);
  if (idx < 0) return null;

  const baseId =
    Math.max(
      0,
      ...all.flatMap((r) =>
        Array.isArray(r.items) ? r.items.map((it) => Number(it.id) || 0) : [],
      ),
    ) + 1;

  const normalized = (Array.isArray(newItems) ? newItems : []).map((it, i) => ({
    id: baseId + i,
    receipt_id: rid,
    item_name: it?.item_name ?? null,
    quantity:
      typeof it?.quantity === "number" ? it.quantity : (it?.quantity ?? null),
    unit_price:
      typeof it?.unit_price === "number"
        ? it.unit_price
        : (it?.unit_price ?? null),
    total_price:
      typeof it?.total_price === "number"
        ? it.total_price
        : (it?.total_price ?? null),
  }));

  all[idx] = { ...all[idx], items: normalized };
  saveAll(all);
  return normalized;
}

export function demoSpendingByItem() {
  const all = loadAll();
  const map = new Map();
  for (const r of all) {
    for (const it of Array.isArray(r.items) ? r.items : []) {
      const name = String(it.item_name || "(Không rõ)");
      const cur = map.get(name) || 0;
      map.set(name, cur + (Number(it.total_price) || 0));
    }
  }
  return Array.from(map.entries())
    .map(([item_name, total_spent]) => ({ item_name, total_spent }))
    .sort((a, b) => (b.total_spent || 0) - (a.total_spent || 0));
}

export function demoCategoryTotals() {
  const all = loadAll();
  const totals = { "Ăn uống": 0, "Mua sắm": 0, Khác: 0 };
  for (const r of all) {
    const g = groupFromCategory(r.category);
    totals[g] = (totals[g] || 0) + (Number(r.total_amount) || 0);
  }
  return {
    groups: Object.entries(totals)
      .map(([group, total]) => ({ group, total }))
      .sort((a, b) => (b.total || 0) - (a.total || 0)),
  };
}

export function demoUploadReceipt(_file) {
  const items = loadAll();
  const nextId = Math.max(...items.map((x) => Number(x.id) || 0), 100) + 1;
  const created = {
    id: nextId,
    store_name: "Demo Store",
    date: new Date().toLocaleDateString("vi-VN"),
    total_amount: 123000,
    category: "Khác",
    image_path: "/demo/receipt-1.svg",
    raw_text: "DEMO OCR TEXT",
    created_at: nowIso(),
    items: [
      {
        id: nextId * 100,
        receipt_id: nextId,
        item_name: "Mặt hàng demo",
        quantity: 1,
        unit_price: 123000,
        total_price: 123000,
      },
    ],
  };
  const updated = [created, ...items];
  saveAll(updated);
  return created;
}

export function demoReset() {
  localStorage.removeItem(STORAGE_KEY);
}

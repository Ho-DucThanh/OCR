import { Link, NavLink } from "react-router-dom";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4">
          <Link to="/" className="text-lg font-semibold">
            OCR Receipts Demo
          </Link>
          <nav className="flex gap-3 text-sm">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${isActive ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`
              }
            >
              Bảng chi tiêu
            </NavLink>
            <NavLink
              to="/stats"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${isActive ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`
              }
            >
              Thống kê
            </NavLink>
            <NavLink
              to="/upload"
              className={({ isActive }) =>
                `rounded-md px-3 py-2 ${isActive ? "bg-slate-900 text-white" : "hover:bg-slate-100"}`
              }
            >
              Tải hóa đơn
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>

      {/* <footer className="border-t bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-slate-500">
          Backend: FastAPI + MySQL • OCR: Tesseract
        </div>
      </footer> */}
    </div>
  );
}

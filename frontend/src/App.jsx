import { Navigate, Route, Routes } from "react-router-dom";

import Layout from "./components/Layout";
import ReceiptDetailPage from "./pages/ReceiptDetailPage";
import ReceiptsPage from "./pages/ReceiptsPage";
import StatsPage from "./pages/StatsPage";
import UploadPage from "./pages/UploadPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<ReceiptsPage />} />
        <Route path="/stats" element={<StatsPage />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/receipts/:id" element={<ReceiptDetailPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Layout>
  );
}

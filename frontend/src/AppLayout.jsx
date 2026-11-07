import { Outlet } from "react-router-dom";
import Sidebar from "./pages/Sidebar";
import "./styles/AppLayout.css";

export default function AppLayout() {
  return (
    <div className="app-layout">
      <Sidebar />

      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}

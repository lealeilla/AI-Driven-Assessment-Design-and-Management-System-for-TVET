import { Outlet, useLocation } from "react-router-dom";
import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";

const pageTitles = {
  "/dashboard": "Dashboard",
  "/generate-assessment": "Generate Assessment",
  "/generated-exams": "Generated Exams",
  "/mark-scripts": "Mark Scripts",
  "/mark-scripts/review": "AI-Assisted Marking",
  "/analytics": "Analytics"
};

function DashboardLayout({ onLogout, user }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();

  return (
    <div className="h-screen overflow-hidden bg-transparent md:flex">
      <Sidebar
        mobileOpen={mobileOpen}
        onClose={() => setMobileOpen(false)}
        onLogout={onLogout}
      />
      <main className="flex h-screen flex-1 flex-col overflow-hidden p-4 md:p-6">
        <Navbar
          title={pageTitles[location.pathname] || "Assessment Workspace"}
          onMenuClick={() => setMobileOpen(true)}
          user={user}
        />
        <div className="mt-5 flex-1 overflow-y-auto overflow-x-hidden pr-1">
          <Outlet />
          <footer className="mt-6 rounded-[24px] border border-sky-100 bg-white/85 px-5 py-4 text-center text-sm text-slate-600 shadow-soft backdrop-blur">
            Designed by Lea Ishimwe
          </footer>
        </div>
      </main>
    </div>
  );
}

export default DashboardLayout;

import { NavLink } from "react-router-dom";

const navItems = [
  { label: "Dashboard", path: "/dashboard" },
  { label: "Generate Assessment", path: "/generate-assessment" },
  { label: "Generated Exams", path: "/generated-exams" },
  { label: "Mark Scripts", path: "/mark-scripts" },
  { label: "Analytics", path: "/analytics" }
];

function Sidebar({ mobileOpen, onClose, onLogout }) {
  return (
    <>
      <div
        className={`fixed inset-0 z-30 bg-slate-900/40 transition md:hidden ${
          mobileOpen ? "opacity-100" : "pointer-events-none opacity-0"
        }`}
        onClick={onClose}
      />
      <aside
        className={`fixed left-0 top-0 z-40 flex h-full w-72 flex-col bg-gradient-to-b from-blue-950 via-sky-900 to-slate-950 px-6 py-7 text-white shadow-soft transition-transform md:static md:w-72 md:translate-x-0 ${
          mobileOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="mb-8 rounded-[24px] border border-sky-200/20 bg-white/10 p-4 backdrop-blur">
          <p className="text-xs uppercase tracking-[0.25em] text-sky-200">TVET Rwanda</p>
          <h1 className="mt-2 text-xl font-semibold leading-tight">
            Assessment Design and Management
          </h1>
          <p className="mt-2 text-sm text-sky-50/80">
            Paper-based exam design, script review, and teacher-controlled AI support.
          </p>
        </div>

        <nav className="flex-1 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === "/dashboard"}
              onClick={onClose}
              className={({ isActive }) =>
                `block rounded-2xl px-4 py-3 text-sm font-medium transition ${
                  isActive
                    ? "bg-white text-blue-950 shadow-lg shadow-sky-900/20"
                    : "text-slate-100 hover:bg-white/10 hover:text-white"
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <button
          type="button"
          onClick={onLogout}
          className="rounded-[24px] border border-emerald-300/30 bg-emerald-400 px-4 py-3 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300"
        >
          Logout
        </button>
      </aside>
    </>
  );
}

export default Sidebar;

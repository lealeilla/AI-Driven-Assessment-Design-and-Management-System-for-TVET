function Navbar({ title, onMenuClick, user }) {
  return (
    <header className="sticky top-4 z-20 flex items-center justify-between rounded-[28px] border border-sky-100 bg-white/92 px-4 py-3 shadow-soft backdrop-blur md:px-5">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="rounded-xl border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 md:hidden"
        >
          Menu
        </button>
        <div>
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">
            Assessment Management
          </p>
          <h2 className="text-lg font-semibold text-slate-900 md:text-xl">{title}</h2>
          <p className="mt-1 hidden text-sm text-slate-500 md:block">
            Supports teacher-led exam design, script marking, and competency analysis.
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <div className="hidden rounded-2xl bg-gradient-to-r from-sky-50 to-emerald-50 px-4 py-2 text-right lg:block">
          <p className="text-sm font-semibold text-slate-900">Teacher Workspace</p>
          <p className="text-xs text-slate-500">AI-assisted, teacher-approved workflow</p>
        </div>

        <div className="flex items-center gap-3 rounded-2xl border border-sky-100 bg-sky-50/90 px-3 py-2">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-blue-700 to-emerald-600 text-sm font-semibold text-white">
            {user?.name?.slice(0, 1) || "T"}
          </div>
          <div className="hidden text-left sm:block">
            <p className="text-sm font-semibold text-slate-900">
              {user?.name || "Assessment Teacher"}
            </p>
            <p className="text-xs text-slate-500">
              {user?.schoolName || "TVET Institution"} | {user?.role || "Teacher"}
            </p>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;

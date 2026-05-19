function StatCard({ title, value, change, accent }) {
  return (
    <div className="rounded-3xl border border-sky-100 bg-gradient-to-br from-white via-white to-sky-50/70 p-5 shadow-soft transition hover:-translate-y-1">
      <div className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${accent}`}>
        {title}
      </div>
      <p className="mt-5 text-3xl font-semibold text-slate-900">{value}</p>
      <p className="mt-2 text-sm text-slate-500">{change}</p>
    </div>
  );
}

export default StatCard;

function BarChartCard({ title, data, color = "bg-blue-500", formatter = (value) => `${value}%` }) {
  return (
    <div className="rounded-3xl border border-white/70 bg-white/90 p-6 shadow-soft">
      <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
      <div className="mt-6 space-y-4">
        {data.map((item) => (
          <div key={item.label}>
            <div className="mb-2 flex items-center justify-between text-sm">
              <span className="font-medium text-slate-700">{item.label}</span>
              <span className="text-slate-500">{formatter(item.value)}</span>
            </div>
            <div className="h-3 overflow-hidden rounded-full bg-slate-100">
              <div className={`h-full rounded-full ${color}`} style={{ width: `${item.value}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default BarChartCard;

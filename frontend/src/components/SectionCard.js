function SectionCard({ title, description, action, children }) {
  return (
    <section className="rounded-3xl border border-white/70 bg-white/90 p-5 shadow-soft md:p-6">
      <div className="mb-5 flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-900 md:text-lg">{title}</h3>
          {description ? <p className="mt-1 text-sm text-slate-500">{description}</p> : null}
        </div>
        {action ? <div>{action}</div> : null}
      </div>
      {children}
    </section>
  );
}

export default SectionCard;

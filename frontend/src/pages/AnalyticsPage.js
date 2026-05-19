import BarChartCard from "../components/BarChartCard";
import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";
import {
  analyticsSummary,
  competencyPerformance,
  strengthWeakness
} from "../data/mockData";

function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-3">
        {analyticsSummary.map((card) => (
          <StatCard
            key={card.title}
            title={card.title}
            value={card.value}
            change={card.note}
            accent="bg-cyan-100 text-cyan-700"
          />
        ))}
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <BarChartCard
          title="Performance by Competency"
          data={competencyPerformance}
          color="bg-cyan-500"
        />

        <SectionCard
          title="Strong vs Weak Areas"
          description="Supports competency-based assessment analysis."
        >
          <div className="space-y-5">
            {strengthWeakness.map((item) => (
              <div key={item.area}>
                <div className="mb-2 flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-700">{item.area}</span>
                  <span className="text-slate-500">
                    Strong {item.strong}% / Weak {item.weak}%
                  </span>
                </div>
                <div className="flex h-3 overflow-hidden rounded-full bg-slate-100">
                  <div className="bg-emerald-500" style={{ width: `${item.strong}%` }} />
                  <div className="bg-rose-400" style={{ width: `${item.weak}%` }} />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </div>
  );
}

export default AnalyticsPage;

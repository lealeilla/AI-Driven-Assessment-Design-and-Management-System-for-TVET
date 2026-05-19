import SectionCard from "../components/SectionCard";
import StatCard from "../components/StatCard";
import { quickStats } from "../data/mockData";

function DashboardPage({ user }) {
  const workflowItems = [
    "Select level, program, and module to generate an exam draft.",
    "Review the generated paper and confirm the writing-space layout.",
    "Download the exam as a structured PDF for printing and classroom use.",
    "Upload scanned student scripts and validate AI marking suggestions."
  ];

  const focusItems = [
    "AI generates questions from curriculum data and past exam papers.",
    "Bloom's Taxonomy is used to move from low-order to high-order thinking.",
    "AI assists marking at 70%, while teachers validate and finalize the remaining 30%."
  ];

  return (
    <div className="space-y-6">
      <section className="rounded-[28px] border border-sky-200/80 bg-gradient-to-r from-blue-950 via-blue-800 to-emerald-700 p-5 text-white shadow-soft">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="max-w-2xl">
            <p className="text-xs uppercase tracking-[0.25em] text-sky-100">Welcome Back</p>
            <h1 className="mt-2 text-xl font-semibold md:text-2xl">
              {user.role} workspace for AI-supported TVET assessment management
            </h1>
            <p className="mt-2 text-sm text-sky-50/95">
              The main purpose of this system is to help teachers generate paper-based exams, manage scanned scripts, validate AI marking, and analyze competency-based results in one professional workspace.
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2">
            <button className="rounded-2xl bg-white px-5 py-3 text-sm font-semibold text-blue-900 transition hover:bg-sky-50">
              Generate New Exam
            </button>
            <button className="rounded-2xl bg-emerald-400 px-5 py-3 text-sm font-semibold text-emerald-950 transition hover:bg-emerald-300">
              Review Marking
            </button>
          </div>
        </div>
      </section>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {quickStats.map((card) => (
          <StatCard key={card.title} {...card} />
        ))}
      </div>

      <SectionCard
        title="Teacher Flow and System Focus"
        description="Both panels stay compact, scrollable, and easy to scan."
      >
        <div className="grid gap-5 xl:grid-cols-2">
          <div className="rounded-[26px] border border-sky-100 bg-gradient-to-b from-sky-50 to-white p-4">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-base font-semibold text-blue-950">Teacher Flow</h3>
              <span className="rounded-full bg-sky-100 px-3 py-1 text-xs font-semibold text-sky-700">
                4 steps
              </span>
            </div>
            <div className="max-h-72 space-y-3 overflow-y-auto pr-1">
              {workflowItems.map((item, index) => (
                <div
                  key={item}
                  className="rounded-2xl border border-sky-100 bg-white p-4 text-sm text-slate-700"
                >
                  <span className="mb-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-blue-700 text-xs font-semibold text-white">
                    {index + 1}
                  </span>
                  <p>{item}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="rounded-[26px] border border-emerald-100 bg-gradient-to-b from-emerald-50 to-white p-4">
            <div className="mb-4 flex items-center justify-between">
              <h3 className="text-base font-semibold text-blue-950">System Focus</h3>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
                Teacher-led
              </span>
            </div>
            <div className="max-h-72 space-y-3 overflow-y-auto pr-1">
              {focusItems.map((item) => (
                <div
                  key={item}
                  className="rounded-2xl border border-emerald-100 bg-white p-4 text-sm text-slate-700"
                >
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </SectionCard>
    </div>
  );
}

export default DashboardPage;

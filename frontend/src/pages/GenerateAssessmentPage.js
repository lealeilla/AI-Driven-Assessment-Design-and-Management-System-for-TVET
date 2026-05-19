import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SectionCard from "../components/SectionCard";
import SelectInput from "../components/SelectInput";
import FormInput from "../components/FormInput";
import { generateExam, getModules } from "../services/api";
import { bloomStages } from "../data/mockData";

function GenerateAssessmentPage() {
  const navigate = useNavigate();

  // ── Modules from backend ─────────────────────────────────────────────
  const [modules, setModules] = useState([]);
  const [loadingModules, setLoadingModules] = useState(true);

  // ── Teacher selections ───────────────────────────────────────────────
  const [selection, setSelection] = useState({
    program: "",
    level: "",
    module: "",
    learning_outcome: "all",
    num_questions: 20,
    total_marks: 100,
    exam_date: "",
    time_allowed: "3 Hours",
  });

  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // ── Load modules on mount ────────────────────────────────────────────
  useEffect(() => {
    getModules()
      .then((data) => {
        setModules(data);
        if (data.length > 0) {
          setSelection((c) => ({
            ...c,
            program: data[0].program,
            level: String(data[0].level),
            module: data[0].module,
          }));
        }
      })
      .catch(() => setError("Could not load modules from server"))
      .finally(() => setLoadingModules(false));
  }, []);

  // ── Available outcomes for selected module ───────────────────────────
  const selectedModuleData = modules.find(
    (m) => m.module === selection.module
  );
  const availableOutcomes = selectedModuleData
    ? selectedModuleData.outcomes
    : ["all"];

  const handleChange = (key, value) => {
    setSelection((c) => {
      if (key === "module") {
        const mod = modules.find((m) => m.module === value);
        return {
          ...c,
          module: value,
          program: mod ? mod.program : c.program,
          level: mod ? String(mod.level) : c.level,
          learning_outcome: "all",
        };
      }
      return { ...c, [key]: value };
    });
  };

  // ── Generate exam ────────────────────────────────────────────────────
  const handleGenerate = async () => {
    setError("");
    setSuccess("");

    if (!selection.module) { setError("Please select a module"); return; }
    if (!selection.exam_date) { setError("Please enter exam date"); return; }

    setGenerating(true);
    try {
      const result = await generateExam({
        program         : selection.program,
        level           : parseInt(selection.level),
        module          : selection.module,
        learning_outcome: selection.learning_outcome,
        num_questions   : parseInt(selection.num_questions),
        total_marks     : parseInt(selection.total_marks),
        exam_date       : selection.exam_date,
        time_allowed    : selection.time_allowed,
      });

      setSuccess(
        `Exam generated! ${result.num_questions} questions, ${result.total_marks} marks. Exam ID: ${result.exam_id}`
      );

      // Go to generated exams page after 1.5s
      setTimeout(() => navigate("/generated-exams"), 1500);

    } catch (err) {
      setError(err.message || "Failed to generate exam");
    } finally {
      setGenerating(false);
    }
  };

  const uniqueModules = modules.map((m) => m.module);

  return (
    <div className="space-y-6">
      <SectionCard
        title="Step-by-Step Exam Generation"
        description="Select the teaching context first, then let the system prepare a teacher-review draft."
        action={
          <button
            onClick={handleGenerate}
            disabled={generating || loadingModules}
            className="rounded-2xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400 disabled:opacity-50"
          >
            {generating ? "Generating..." : "Generate Exam"}
          </button>
        }
      >
        {loadingModules ? (
          <div className="py-8 text-center text-sm text-slate-500">Loading modules from backend...</div>
        ) : (
          <>
            {/* Row 1: Module selection */}
            <div className="grid gap-4 md:grid-cols-3">
              <SelectInput
                label="Module"
                value={selection.module}
                onChange={(e) => handleChange("module", e.target.value)}
                options={uniqueModules}
              />
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Program</label>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                  {selection.program || "—"}
                </div>
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Level</label>
                <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700">
                  Level {selection.level || "—"}
                </div>
              </div>
            </div>

            {/* Row 2: Learning outcome */}
            <div className="mt-4 grid gap-4 md:grid-cols-2">
              <SelectInput
                label="Learning Outcome"
                value={selection.learning_outcome}
                onChange={(e) => handleChange("learning_outcome", e.target.value)}
                options={availableOutcomes}
              />
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Assessment Type</label>
                <div className={`rounded-2xl border px-4 py-3 text-sm font-semibold ${
                  selection.learning_outcome === "all"
                    ? "border-cyan-200 bg-cyan-50 text-cyan-700"
                    : "border-blue-200 bg-blue-50 text-blue-700"
                }`}>
                  {selection.learning_outcome === "all" ? "Summative (all outcomes)" : "Formative (single outcome)"}
                </div>
              </div>
            </div>

            {/* Row 3: Exam settings */}
            <div className="mt-4 grid gap-4 md:grid-cols-4">
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Number of Questions</label>
                <input
                  type="number" min={5} max={50}
                  value={selection.num_questions}
                  onChange={(e) => handleChange("num_questions", e.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:border-cyan-300"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Total Marks</label>
                <input
                  type="number" min={10} max={200}
                  value={selection.total_marks}
                  onChange={(e) => handleChange("total_marks", e.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:border-cyan-300"
                />
              </div>
              <div>
                <label className="mb-2 block text-sm font-medium text-slate-700">Exam Date</label>
                <input
                  type="date"
                  value={selection.exam_date}
                  onChange={(e) => handleChange("exam_date", e.target.value)}
                  className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 outline-none focus:border-cyan-300"
                />
              </div>
              <SelectInput
                label="Time Allowed"
                value={selection.time_allowed}
                onChange={(e) => handleChange("time_allowed", e.target.value)}
                options={["1 Hour", "1 Hour 30 Minutes", "2 Hours", "2 Hours 30 Minutes", "3 Hours"]}
              />
            </div>

            {/* Status messages */}
            {error && (
              <div className="mt-4 rounded-2xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
                {error}
              </div>
            )}
            {success && (
              <div className="mt-4 rounded-2xl bg-green-50 border border-green-200 px-4 py-3 text-sm text-green-700">
                ✓ {success}
              </div>
            )}

            <div className="mt-6 rounded-3xl border border-cyan-100 bg-cyan-50 p-5 text-sm text-slate-700">
              Questions will be generated from the training manual using Bloom's Taxonomy.
              {selection.learning_outcome !== "all" && (
                <span className="ml-1 font-medium text-cyan-700">
                  Formative mode — questions focused on: {selection.learning_outcome}
                </span>
              )}
            </div>
          </>
        )}
      </SectionCard>

      <SectionCard
        title="Bloom's Taxonomy Coverage"
        description="Questions progress from lower-order to higher-order thinking skills."
      >
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {bloomStages.map((stage, index) => (
            <div key={stage.name} className="flex items-start gap-4 rounded-2xl border border-slate-200 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-slate-950 text-sm font-semibold text-white">
                {index + 1}
              </div>
              <div>
                <h4 className="text-sm font-semibold text-slate-900">{stage.name}</h4>
                <p className="mt-1 text-sm text-slate-600">{stage.focus}</p>
              </div>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}

export default GenerateAssessmentPage;
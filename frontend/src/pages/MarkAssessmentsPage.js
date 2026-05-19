import { useState } from "react";
import { Link } from "react-router-dom";
import FormInput from "../components/FormInput";
import SectionCard from "../components/SectionCard";
import { uploadQueue } from "../data/mockData";

function MarkAssessmentsPage() {
  const [studentName, setStudentName] = useState("");

  return (
    <div className="space-y-6">
      <SectionCard
        title="Upload Scanned Scripts"
        description="Upload scanned PDF or image files for AI-assisted review."
      >
        <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
          <form className="space-y-5 rounded-3xl border border-slate-200 p-5">
            <FormInput
              label="Student Name"
              name="studentName"
              placeholder="Enter student name"
              value={studentName}
              onChange={(event) => setStudentName(event.target.value)}
            />

            <label className="block">
              <span className="mb-2 block text-sm font-medium text-slate-700">Scanned Script</span>
              <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-6 text-sm text-slate-500">
                Upload scanned PDF/image
              </div>
            </label>

            <button
              type="button"
              className="rounded-2xl bg-cyan-500 px-5 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-400"
            >
              Submit
            </button>
          </form>

          <div className="rounded-3xl bg-slate-50 p-5">
            <h3 className="text-base font-semibold text-slate-900">Why this matters</h3>
            <div className="mt-4 space-y-3 text-sm text-slate-600">
              <div className="rounded-2xl bg-white p-4">
                Scripts remain paper-based; the system only supports upload after the exam is written.
              </div>
              <div className="rounded-2xl bg-white p-4">
                AI reads the scanned response and suggests marks, but the teacher must review every result.
              </div>
              <div className="rounded-2xl bg-white p-4">
                This keeps the process practical for TVET institutions that still assess on paper.
              </div>
            </div>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="Recent Upload Queue"
        description="Mock uploads currently waiting in the teacher workflow."
        action={
          <Link
            to="/mark-scripts/review"
            className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 transition hover:border-cyan-300 hover:text-cyan-700"
          >
            Open AI Marking Review
          </Link>
        }
      >
        <div className="space-y-3">
          {uploadQueue.map((item) => (
            <div
              key={item.id}
              className="flex flex-col gap-3 rounded-2xl border border-slate-200 p-4 md:flex-row md:items-center md:justify-between"
            >
              <div>
                <p className="font-semibold text-slate-900">{item.student}</p>
                <p className="text-sm text-slate-500">{item.file}</p>
              </div>
              <span className="rounded-full bg-cyan-50 px-3 py-1 text-xs font-semibold text-cyan-700">
                {item.status}
              </span>
            </div>
          ))}
        </div>
      </SectionCard>
    </div>
  );
}

export default MarkAssessmentsPage;

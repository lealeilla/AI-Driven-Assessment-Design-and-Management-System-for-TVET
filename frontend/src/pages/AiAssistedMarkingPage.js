import { useState } from "react";
import DataTable from "../components/DataTable";
import SectionCard from "../components/SectionCard";
import { markingRows } from "../data/mockData";

function AiAssistedMarkingPage() {
  const [rows, setRows] = useState(markingRows);

  const handleMarkChange = (id, value) => {
    setRows((current) =>
      current.map((row) =>
        row.id === id ? { ...row, finalMark: value === "" ? "" : Number(value) } : row
      )
    );
  };

  const columns = [
    { key: "question", label: "Question" },
    { key: "answer", label: "Student Answer" },
    { key: "aiMark", label: "AI Suggested Mark" },
    { key: "finalMark", label: "Teacher Final Mark" }
  ];

  return (
    <div className="space-y-6">
      <SectionCard
        title="AI-Assisted Marking"
        description="Review the extracted answers and confirm the final scores."
        action={
          <button className="rounded-2xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950">
            Approve Results
          </button>
        }
      >
        <div className="mb-5 rounded-3xl border border-cyan-100 bg-cyan-50 p-5 text-sm text-slate-700">
          AI assists marking (70%), teacher validates (30%).
        </div>

        <DataTable
          columns={columns}
          rows={rows}
          renderCell={(row, key) => {
            if (key === "aiMark") {
              return <span className="font-semibold text-cyan-700">{row.aiMark}</span>;
            }

            if (key === "finalMark") {
              return (
                <input
                  type="number"
                  min="0"
                  value={row.finalMark}
                  onChange={(event) => handleMarkChange(row.id, event.target.value)}
                  className="w-24 rounded-xl border border-slate-200 px-3 py-2 outline-none focus:border-cyan-500"
                />
              );
            }

            if (key === "answer") {
              return <p className="max-w-xl leading-6 text-slate-600">{row.answer}</p>;
            }

            return row[key];
          }}
        />
      </SectionCard>
    </div>
  );
}

export default AiAssistedMarkingPage;

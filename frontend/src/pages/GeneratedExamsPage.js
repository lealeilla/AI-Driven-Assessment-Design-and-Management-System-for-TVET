import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SectionCard from "../components/SectionCard";
import { getMyExams, deleteExam, downloadExamPDF, downloadMarkingGuide } from "../services/api";

function GeneratedExamsPage() {
  const navigate = useNavigate();
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedExam, setSelectedExam] = useState(null);
  const [editingExam, setEditingExam] = useState(null);
  const [editData, setEditData] = useState({});

  // ── Fetch exams on mount ────────────────────────────────────────────
  useEffect(() => {
    fetchExams();
  }, []);

  const fetchExams = async () => {
    setLoading(true);
    try {
      const data = await getMyExams();
      setExams(data);
      setError("");
    } catch (err) {
      setError(err.message || "Failed to load exams");
    } finally {
      setLoading(false);
    }
  };

  // ── Delete exam ─────────────────────────────────────────────────────
  const handleDelete = async (examId) => {
    if (!window.confirm("Are you sure you want to delete this exam?")) return;
    try {
      await deleteExam(examId);
      await fetchExams();
      if (selectedExam?.id === examId) setSelectedExam(null);
    } catch (err) {
      alert("Failed to delete exam: " + err.message);
    }
  };

  // ── Edit exam ──────────────────────────────────────────────────────
  const handleEditClick = (exam) => {
    setEditingExam(exam.id);
    setEditData({
      exam_date: exam.exam_date || "",
      time_allowed: exam.time_allowed || "3 Hours",
      total_marks: exam.total_marks || 100,
      learning_outcome: exam.learning_outcome || "",
    });
  };

  const handleEditSave = async (examId) => {
    try {
      await updateExam(examId, editData);
      setEditingExam(null);
      await fetchExams();
    } catch (err) {
      alert("Failed to update exam: " + err.message);
    }
  };

  const handleEditCancel = () => {
    setEditingExam(null);
  };

  // ── Select exam for preview ────────────────────────────────────────
  const handleSelectExam = (exam) => {
    setSelectedExam(exam);
  };

  // ── Loading state ──────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <div className="text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-200 border-t-blue-700"></div>
          <p className="mt-3 text-sm text-slate-500">Loading exams...</p>
        </div>
      </div>
    );
  }

  // ── Error state ────────────────────────────────────────────────────
  if (error) {
    return (
      <div className="rounded-2xl bg-red-50 border border-red-200 p-6 text-center">
        <p className="text-red-700">{error}</p>
        <button
          onClick={fetchExams}
          className="mt-3 rounded-xl bg-red-100 px-4 py-2 text-sm font-semibold text-red-700 hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <SectionCard
        title="Generated Exams"
        description="Recent AI-prepared papers ready for teacher review and paper-based delivery."
        action={
          <button
            onClick={() => navigate("/generate-assessment")}
            className="rounded-2xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-cyan-400"
          >
            Generate New Exam
          </button>
        }
      >
        {exams.length === 0 ? (
          <div className="py-12 text-center">
            <p className="text-slate-500">No exams generated yet.</p>
            <button
              onClick={() => navigate("/generate-assessment")}
              className="mt-3 rounded-xl bg-blue-100 px-4 py-2 text-sm font-semibold text-blue-700 hover:bg-blue-200"
            >
              Generate Your First Exam
            </button>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {exams.map((exam) => (
              <div
                key={exam.id}
                className={`relative rounded-3xl border p-5 transition-all hover:shadow-md ${
                  selectedExam?.id === exam.id
                    ? "border-cyan-400 bg-cyan-50"
                    : "border-slate-100 bg-white"
                }`}
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-slate-400">
                        {exam.id ? `EX-${exam.id}` : "—"}
                      </span>
                      <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                        {exam.assessment_type || "Formative"}
                      </span>
                    </div>
                    <h3 className="mt-2 text-base font-semibold text-slate-900">
                      {exam.module || "Untitled Exam"}
                    </h3>
                    <p className="mt-1 text-sm text-slate-500">
                      Level {exam.level || "—"}
                    </p>
                    <div className="mt-3 flex flex-wrap gap-x-4 gap-y-2 text-xs text-slate-500">
                      <span>{exam.num_questions || 0} questions</span>
                      <span>{exam.total_marks || 0} marks</span>
                      <span>
                        {exam.exam_date
                          ? new Date(exam.exam_date).toLocaleDateString()
                          : "No date set"}
                      </span>
                    </div>
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => handleSelectExam(exam)}
                      className="rounded-xl border border-cyan-200 px-3 py-1.5 text-xs font-medium text-cyan-700 hover:bg-cyan-50"
                    >
                      Preview
                    </button>
                  </div>
                </div>

                {/* ── Edit / Delete Buttons ──────────────────────────────────── */}
                <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-4">
                  <button
                    onClick={() => handleEditClick(exam)}
                    className="rounded-xl border border-amber-200 bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-700 hover:bg-amber-100"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(exam.id)}
                    className="rounded-xl border border-red-200 bg-red-50 px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-100"
                  >
                    Delete
                  </button>
                </div>

                {/* ── Inline Edit Form ────────────────────────────────────── */}
                {editingExam === exam.id && (
                  <div className="mt-3 rounded-2xl border border-amber-100 bg-amber-50 p-4">
                    <div className="grid gap-3 md:grid-cols-2">
                      <div>
                        <label className="mb-1 block text-xs font-medium text-amber-800">
                          Exam Date
                        </label>
                        <input
                          type="date"
                          value={editData.exam_date}
                          onChange={(e) =>
                            setEditData({ ...editData, exam_date: e.target.value })
                          }
                          className="w-full rounded-xl border border-amber-200 bg-white px-3 py-2 text-xs"
                        />
                      </div>
                      <div>
                        <label className="mb-1 block text-xs font-medium text-amber-800">
                          Time Allowed
                        </label>
                        <select
                          value={editData.time_allowed}
                          onChange={(e) =>
                            setEditData({ ...editData, time_allowed: e.target.value })
                          }
                          className="w-full rounded-xl border border-amber-200 bg-white px-3 py-2 text-xs"
                        >
                          <option>1 Hour</option>
                          <option>1 Hour 30 Minutes</option>
                          <option>2 Hours</option>
                          <option>2 Hours 30 Minutes</option>
                          <option>3 Hours</option>
                        </select>
                      </div>
                      <div>
                        <label className="mb-1 block text-xs font-medium text-amber-800">
                          Total Marks
                        </label>
                        <input
                          type="number"
                          value={editData.total_marks}
                          onChange={(e) =>
                            setEditData({ ...editData, total_marks: parseInt(e.target.value) })
                          }
                          className="w-full rounded-xl border border-amber-200 bg-white px-3 py-2 text-xs"
                        />
                      </div>
                    </div>
                    <div className="mt-3 flex gap-2">
                      <button
                        onClick={() => handleEditSave(exam.id)}
                        className="rounded-xl bg-amber-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-amber-700"
                      >
                        Save
                      </button>
                      <button
                        onClick={handleEditCancel}
                        className="rounded-xl bg-slate-200 px-4 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-300"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </SectionCard>

      {/* ── Exam Preview ──────────────────────────────────────────────────────── */}
      {selectedExam && (
        <SectionCard
          title={`Exam Preview — EX-${selectedExam.id}`}
          description={`${selectedExam.assessment_type || "Formative"} assessment for ${selectedExam.module || "Untitled Exam"}`}
          action={
            <div className="flex gap-2">
              <button
                onClick={() => downloadMarkingGuide(selectedExam.id)}
                className="rounded-2xl bg-white border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
              >
                Download Marking Guide
              </button>
              <button
                onClick={() => downloadExamPDF(selectedExam.id)}
                className="rounded-2xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-white hover:bg-cyan-400"
              >
                Download PDF
              </button>
            </div>
          }
        >
          <div className="rounded-3xl border border-slate-200 bg-white p-6 text-center">
            <p className="text-xs uppercase tracking-[0.25em] text-slate-400">
              {selectedExam.school_name || "RWANDA TVET BOARD"}
            </p>
            <h2 className="mt-2 text-xl font-semibold text-slate-900">
              {selectedExam.module || "Exam"}
            </h2>
            <div className="mt-4 flex flex-wrap justify-center gap-4 text-sm text-slate-500">
              <span>Level {selectedExam.level || "—"}</span>
              <span>{selectedExam.assessment_type || "Formative"}</span>
              <span>{selectedExam.num_questions || 0} questions</span>
              <span>Total: {selectedExam.total_marks || 0} marks</span>
              <span>
                {selectedExam.exam_date
                  ? new Date(selectedExam.exam_date).toLocaleDateString()
                  : "No date set"}
              </span>
            </div>
          </div>
        </SectionCard>
      )}
    </div>
  );
}

export default GeneratedExamsPage;
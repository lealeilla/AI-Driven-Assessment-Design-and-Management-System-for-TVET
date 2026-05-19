import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import SectionCard from "../components/SectionCard";
import { downloadExamPDF, downloadMarkingGuide, getMyExams } from "../services/api";

function GeneratedExamsPage() {
  const [exams, setExams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedExam, setSelectedExam] = useState(null);
  const [downloading, setDownloading] = useState("");

  useEffect(() => {
    getMyExams()
      .then((data) => {
        setExams(data);
        if (data.length > 0) setSelectedExam(data[0]);
      })
      .catch(() => setError("Could not load exams"))
      .finally(() => setLoading(false));
  }, []);

  const handleDownloadPDF = async (examId) => {
    setDownloading("pdf");
    try {
      await downloadExamPDF(examId);
    } catch (err) {
      setError("Failed to download PDF: " + err.message);
    } finally {
      setDownloading("");
    }
  };

  const handleDownloadGuide = async (examId) => {
    setDownloading("guide");
    try {
      await downloadMarkingGuide(examId);
    } catch (err) {
      setError("Failed to download marking guide: " + err.message);
    } finally {
      setDownloading("");
    }
  };

  const formatDate = (dateStr) => {
    try {
      return new Date(dateStr).toLocaleDateString("en-GB", {
        day: "2-digit", month: "short", year: "numeric"
      }).toUpperCase();
    } catch { return dateStr; }
  };

  return (
    <div className="space-y-6">
      <SectionCard
        title="Generated Exams"
        description="Recent AI-prepared papers ready for teacher review and paper-based delivery."
      >
        {loading ? (
          <div className="py-8 text-center text-sm text-slate-500">Loading your exams...</div>
        ) : error ? (
          <div className="rounded-2xl bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">{error}</div>
        ) : exams.length === 0 ? (
          <div className="py-8 text-center">
            <p className="text-sm text-slate-500">No exams generated yet.</p>
            <Link to="/generate-assessment"
              className="mt-3 inline-block rounded-2xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950">
              Generate Your First Exam
            </Link>
          </div>
        ) : (
          <div className="grid gap-4 md:grid-cols-3">
            {exams.map((exam) => (
              <button
                key={exam.id}
                onClick={() => setSelectedExam(exam)}
                className={`rounded-3xl border p-5 text-left transition hover:border-cyan-300 ${
                  selectedExam?.id === exam.id
                    ? "border-cyan-400 bg-cyan-50"
                    : "border-slate-200 bg-white"
                }`}
              >
                <div className="flex items-center justify-between gap-3">
                  <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                    EX-{exam.id}
                  </span>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                    exam.assessment_type === "Summative"
                      ? "bg-cyan-50 text-cyan-700"
                      : "bg-blue-50 text-blue-700"
                  }`}>
                    {exam.assessment_type}
                  </span>
                </div>
                <h3 className="mt-4 text-base font-semibold text-slate-900">{exam.module}</h3>
                <p className="mt-1 text-sm text-slate-500">Level {exam.level}</p>
                <div className="mt-3 flex items-center justify-between">
                  <span className="text-xs text-slate-400">{exam.num_questions} questions</span>
                  <span className="text-xs font-semibold text-slate-600">{exam.total_marks} marks</span>
                </div>
                <p className="mt-2 text-xs uppercase tracking-[0.2em] text-slate-400">
                  {formatDate(exam.created_at)}
                </p>
              </button>
            ))}
          </div>
        )}
      </SectionCard>

      {selectedExam && (
        <SectionCard
          title={`Exam Preview — EX-${selectedExam.id}`}
          description={`${selectedExam.assessment_type} assessment for ${selectedExam.module}`}
          action={
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => handleDownloadGuide(selectedExam.id)}
                disabled={downloading === "guide"}
                className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700 hover:border-slate-300 disabled:opacity-50"
              >
                {downloading === "guide" ? "Downloading..." : "Download Marking Guide"}
              </button>
              <button
                onClick={() => handleDownloadPDF(selectedExam.id)}
                disabled={downloading === "pdf"}
                className="rounded-2xl bg-cyan-500 px-4 py-2 text-sm font-semibold text-slate-950 hover:bg-cyan-400 disabled:opacity-50"
              >
                {downloading === "pdf" ? "Downloading..." : "Download PDF"}
              </button>
            </div>
          }
        >
          <div className="rounded-[30px] border border-slate-200 bg-white p-6">
            <div className="border-b border-slate-200 pb-5 text-center">
              <p className="text-sm uppercase tracking-[0.3em] text-slate-400">Rwanda TVET Board</p>
              <h2 className="mt-2 text-2xl font-semibold text-slate-950">
                {selectedExam.module}
              </h2>
              <div className="mt-4 flex flex-wrap justify-center gap-3 text-sm text-slate-600">
                <span className="rounded-full bg-slate-100 px-4 py-2">Level {selectedExam.level}</span>
                <span className="rounded-full bg-slate-100 px-4 py-2">{selectedExam.assessment_type}</span>
                <span className="rounded-full bg-slate-100 px-4 py-2">{selectedExam.num_questions} questions</span>
                <span className="rounded-full bg-slate-100 px-4 py-2">Total: {selectedExam.total_marks} marks</span>
                <span className="rounded-full bg-slate-100 px-4 py-2">Date: {selectedExam.exam_date}</span>
              </div>
            </div>

            <div className="mt-6 rounded-3xl bg-slate-50 p-5">
              <p className="text-sm text-slate-600">
                Click <strong>Download PDF</strong> to get the printable exam paper, or
                <strong> Download Marking Guide</strong> for the teacher answer sheet.
              </p>
            </div>
          </div>
        </SectionCard>
      )}

      <SectionCard
        title="Teacher Control Reminder"
        description="This remains a support tool, not a replacement for teacher judgment."
        action={
          <Link to="/mark-scripts"
            className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-medium text-slate-700">
            Continue to Mark Scripts
          </Link>
        }
      >
        <p className="text-sm text-slate-600">
          Teachers can review questions and decide when a generated paper is ready for printing and assessment use.
        </p>
      </SectionCard>
    </div>
  );
}

export default GeneratedExamsPage;
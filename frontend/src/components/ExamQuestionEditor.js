import { useState, useEffect } from "react";
import SectionCard from "./SectionCard";
import { getExamQuestions, updateQuestion, deleteQuestion } from "../services/api";

function ExamQuestionEditor({ examId }) {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState(null);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    fetchQuestions();
  }, [examId]);

  const fetchQuestions = async () => {
    setLoading(true);
    try {
      const data = await getExamQuestions(examId);
      setQuestions(data);
    } catch (err) {
      console.error("Failed to load questions:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditClick = (q) => {
    setEditingId(q.id);
    setEditData({
      question: q.question,
      question_type: q.question_type,
      options: q.options || [],
      correct_answer: q.correct_answer,
      marks: q.marks,
      bloom_level: q.bloom_level,
      topic: q.topic,
    });
  };

  const handleEditSave = async (questionId) => {
    try {
      await updateQuestion(questionId, editData);
      setEditingId(null);
      await fetchQuestions();
    } catch (err) {
      alert("Failed to update question: " + err.message);
    }
  };

  const handleEditCancel = () => {
    setEditingId(null);
  };

  const handleDelete = async (questionId) => {
    if (!window.confirm("Delete this question?")) return;
    try {
      await deleteQuestion(questionId);
      await fetchQuestions();
    } catch (err) {
      alert("Failed to delete question: " + err.message);
    }
  };

  if (loading) return <div className="py-8 text-center text-sm text-slate-500">Loading questions...</div>;

  return (
    <div className="space-y-4">
      {questions.length === 0 ? (
        <div className="py-8 text-center text-slate-500">No questions found for this exam.</div>
      ) : (
        questions.map((q) => (
          <div key={q.id} className="rounded-2xl border border-slate-200 bg-white p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-slate-500">#{q.number}</span>
                  <span className="rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">
                    {q.question_type}
                  </span>
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-medium text-emerald-700">
                    {q.bloom_level}
                  </span>
                  <span className="text-xs text-slate-500">{q.marks} marks</span>
                </div>
                <p className="mt-2 text-sm text-slate-800">{q.question}</p>
                {q.options && q.options.length > 0 && (
                  <div className="mt-2 grid gap-1 sm:grid-cols-2">
                    {q.options.map((opt, i) => (
                      <div key={i} className="text-xs text-slate-600">{opt}</div>
                    ))}
                  </div>
                )}
                <div className="mt-1 text-xs text-slate-500">
                  Answer: <span className="font-medium text-slate-800">{q.correct_answer}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleEditClick(q)}
                  className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 hover:bg-amber-100"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDelete(q.id)}
                  className="rounded-lg border border-red-200 bg-red-50 px-3 py-1 text-xs font-medium text-red-700 hover:bg-red-100"
                >
                  Delete
                </button>
              </div>
            </div>

            {editingId === q.id && (
              <div className="mt-3 rounded-xl border border-amber-100 bg-amber-50 p-3">
                <div className="grid gap-2">
                  <textarea
                    value={editData.question}
                    onChange={(e) => setEditData({ ...editData, question: e.target.value })}
                    className="rounded-lg border border-amber-200 bg-white px-3 py-2 text-sm"
                    rows={2}
                  />
                  <div className="flex gap-2">
                    <input
                      value={editData.marks}
                      onChange={(e) => setEditData({ ...editData, marks: parseInt(e.target.value) })}
                      className="w-20 rounded-lg border border-amber-200 bg-white px-2 py-1 text-sm"
                      placeholder="Marks"
                    />
                    <select
                      value={editData.question_type}
                      onChange={(e) => setEditData({ ...editData, question_type: e.target.value })}
                      className="rounded-lg border border-amber-200 bg-white px-2 py-1 text-sm"
                    >
                      <option>mcq</option>
                      <option>true_false</option>
                      <option>open</option>
                      <option>matching</option>
                    </select>
                  </div>
                </div>
                <div className="mt-2 flex gap-2">
                  <button
                    onClick={() => handleEditSave(q.id)}
                    className="rounded-lg bg-amber-600 px-3 py-1 text-xs font-semibold text-white hover:bg-amber-700"
                  >
                    Save
                  </button>
                  <button
                    onClick={handleEditCancel}
                    className="rounded-lg bg-slate-200 px-3 py-1 text-xs font-semibold text-slate-700 hover:bg-slate-300"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        ))
      )}
    </div>
  );
}

export default ExamQuestionEditor;
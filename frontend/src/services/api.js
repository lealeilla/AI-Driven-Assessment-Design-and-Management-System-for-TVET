const BASE_URL = "http://localhost:8000";

// ── Token helpers ──────────────────────────────────────────────────────
const getToken = () => localStorage.getItem("tvet_token");
const setToken = (t) => localStorage.setItem("tvet_token", t);
const removeToken = () => localStorage.removeItem("tvet_token");

// ── Base request ───────────────────────────────────────────────────────
async function request(path, options = {}) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...options.headers };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (res.status === 401) {
    removeToken();
    window.location.href = "/login";
    return;
  }

  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// ── Auth ───────────────────────────────────────────────────────────────
export async function login(email, password) {
  const data = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
  setToken(data.access_token);
  return data;
}

export async function register(name, email, password, school) {
  const data = await request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password, school }),
  });
  setToken(data.access_token);
  return data;
}

export function logout() {
  removeToken();
}

export function isLoggedIn() {
  return !!getToken();
}

// ── Modules ────────────────────────────────────────────────────────────
export async function getModules() {
  return request("/modules");
}

// ── Exam generation ────────────────────────────────────────────────────
export async function generateExam(payload) {
  return request("/exams/generate", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

// ── My exams ───────────────────────────────────────────────────────────
export async function getMyExams() {
  return request("/exams");
}

// ── Download PDF ───────────────────────────────────────────────────────
export async function downloadExamPDF(examId) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/exams/${examId}/pdf`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to download PDF");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `exam_${examId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

// ── Download marking guide ─────────────────────────────────────────────
export async function downloadMarkingGuide(examId) {
  const token = getToken();
  const res = await fetch(`${BASE_URL}/exams/${examId}/marking-guide`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error("Failed to download marking guide");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `marking_guide_${examId}.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}

// ── Question bank ──────────────────────────────────────────────────────
export async function getQuestionBank(filters = {}) {
  const params = new URLSearchParams(filters).toString();
  return request(`/question-bank${params ? "?" + params : ""}`);
}

export async function deleteExam(examId) {
  return request(`/exams/${examId}`, { method: "DELETE" });
}

export async function updateExam(examId, data) {
  return request(`/exams/${examId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function getDashboardStats() {
  return request("/dashboard/stats");
}
export async function updateQuestion(questionId, data) {
  return request(`/questions/${questionId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteQuestion(questionId) {
  return request(`/questions/${questionId}`, { method: "DELETE" });
}
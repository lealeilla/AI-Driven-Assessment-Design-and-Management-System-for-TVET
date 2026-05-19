import { useState } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import DashboardLayout from "./layouts/DashboardLayout";
import AnalyticsPage from "./pages/AnalyticsPage";
import DashboardPage from "./pages/DashboardPage";
import GenerateAssessmentPage from "./pages/GenerateAssessmentPage";
import GeneratedExamsPage from "./pages/GeneratedExamsPage";
import AiAssistedMarkingPage from "./pages/AiAssistedMarkingPage";
import LoginPage from "./pages/LoginPage";
import MarkAssessmentsPage from "./pages/MarkAssessmentsPage";
import { isLoggedIn, logout } from "./services/api";

function App() {
  const [user, setUser] = useState(() => {
    // Restore session if token exists
    if (isLoggedIn()) {
      return { name: "Teacher", role: "Teacher", schoolName: "Rwanda TVET School" };
    }
    return null;
  });

  const handleLogout = () => {
    logout();
    setUser(null);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"
          element={user ? <Navigate to="/dashboard" replace /> : <LoginPage onLogin={setUser} />}
        />
        <Route
          element={
            user
              ? <DashboardLayout onLogout={handleLogout} user={user} />
              : <Navigate to="/login" replace />
          }
        >
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage user={user} />} />
          <Route path="/generate-assessment" element={<GenerateAssessmentPage />} />
          <Route path="/generated-exams" element={<GeneratedExamsPage />} />
          <Route path="/mark-scripts" element={<MarkAssessmentsPage />} />
          <Route path="/mark-scripts/review" element={<AiAssistedMarkingPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
        </Route>
        <Route path="*" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
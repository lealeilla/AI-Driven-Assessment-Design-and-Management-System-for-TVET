import { useState } from "react";
import FormInput from "../components/FormInput";
import { login, register } from "../services/api";

const defaultLoginForm  = { email: "", password: "" };
const defaultRegisterForm = { fullName: "", schoolName: "", email: "", password: "" };

function LoginPage({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [loginForm, setLoginForm] = useState(defaultLoginForm);
  const [registerForm, setRegisterForm] = useState(defaultRegisterForm);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [apiError, setApiError] = useState("");

  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginForm((c) => ({ ...c, [name]: value }));
  };

  const handleRegisterChange = (e) => {
    const { name, value } = e.target;
    setRegisterForm((c) => ({ ...c, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setApiError("");
    const nextErrors = {};

    if (mode === "login") {
      if (!loginForm.email.trim())    nextErrors.email    = "Email is required";
      if (!loginForm.password.trim()) nextErrors.password = "Password is required";
      setErrors(nextErrors);
      if (Object.keys(nextErrors).length > 0) return;

      setLoading(true);
      try {
        const data = await login(loginForm.email, loginForm.password);
        onLogin({
          name: data.teacher_name,
          role: "Teacher",
          email: loginForm.email,
          schoolName: "Rwanda TVET School",
        });
      } catch (err) {
        setApiError(err.message || "Invalid email or password");
      } finally {
        setLoading(false);
      }
      return;
    }

    // Register
    if (!registerForm.fullName.trim())   nextErrors.fullName   = "Names are required";
    if (!registerForm.schoolName.trim()) nextErrors.schoolName = "School name is required";
    if (!registerForm.email.trim())      nextErrors.email      = "Email is required";
    if (!registerForm.password.trim())   nextErrors.password   = "Password is required";
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setLoading(true);
    try {
      const data = await register(
        registerForm.fullName,
        registerForm.email,
        registerForm.password,
        registerForm.schoolName
      );
      onLogin({
        name: data.teacher_name,
        role: "Teacher",
        email: registerForm.email,
        schoolName: registerForm.schoolName,
      });
    } catch (err) {
      setApiError(err.message || "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  const switchMode = (m) => { setMode(m); setErrors({}); setApiError(""); };

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-6 md:px-6">
      <div className="w-full max-w-7xl overflow-hidden rounded-[36px] border border-sky-100 bg-white/92 shadow-soft backdrop-blur">
        <div className="flex items-center justify-between border-b border-sky-100 px-5 py-4 md:px-8">
          <div>
            <p className="text-xs uppercase tracking-[0.24em] text-blue-700">TVET Rwanda</p>
            <h1 className="mt-1 text-lg font-semibold text-slate-900 md:text-xl">
              AI-Driven Assessment Design and Management System
            </h1>
            <p className="mt-1 text-sm text-slate-500">
              Supports teachers in exam generation, script marking, and competency analysis.
            </p>
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={() => switchMode("login")}
              className={`rounded-2xl px-5 py-3 text-sm font-semibold transition ${
                mode === "login" ? "bg-blue-700 text-white" : "bg-sky-50 text-blue-800 hover:bg-sky-100"
              }`}>Login</button>
            <button type="button" onClick={() => switchMode("register")}
              className={`rounded-2xl px-5 py-3 text-sm font-semibold transition ${
                mode === "register" ? "bg-emerald-700 text-white" : "bg-emerald-50 text-emerald-800 hover:bg-emerald-100"
              }`}>Register</button>
          </div>
        </div>

        <div className="grid lg:grid-cols-[1.05fr_0.95fr]">
          <div className="bg-gradient-to-br from-blue-950 via-blue-800 to-emerald-700 px-6 py-8 text-white md:px-8 md:py-10">
            <div className="max-w-xl">
              <p className="text-xs uppercase tracking-[0.24em] text-sky-100">Main Purpose</p>
              <h2 className="mt-2 text-2xl font-semibold md:text-[1.75rem]">
                Help teachers design better paper-based assessments with AI support.
              </h2>
              <p className="mt-3 text-sm leading-7 text-sky-50/95">
                The system brings together curriculum-based exam generation, structured printable papers,
                scanned script uploads, AI-assisted marking, and teacher validation in one platform.
              </p>
            </div>
            <div className="mt-8 grid gap-4 sm:grid-cols-2">
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm font-semibold">Generate Exams</p>
                <p className="mt-2 text-sm text-sky-50/80">Use curriculum and past papers to prepare printable assessments.</p>
              </div>
              <div className="rounded-3xl border border-white/10 bg-white/10 p-5 backdrop-blur">
                <p className="text-sm font-semibold">Teacher Validation</p>
                <p className="mt-2 text-sm text-sky-50/80">Keep final control over marking, approval, and performance review.</p>
              </div>
            </div>
          </div>

          <div className="px-6 py-8 md:px-8 md:py-10">
            <div className="mx-auto max-w-lg">
              <p className="text-xs uppercase tracking-[0.24em] text-slate-500">
                {mode === "login" ? "Teacher Access" : "Teacher Registration"}
              </p>
              <h2 className="mt-2 text-xl font-semibold text-slate-900 md:text-2xl">
                {mode === "login" ? "Login to your workspace" : "Create your teacher account"}
              </h2>

              {apiError && (
                <div className="mt-4 rounded-2xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-200">
                  {apiError}
                </div>
              )}

              <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
                {mode === "register" && (
                  <>
                    <FormInput label="Full Names" name="fullName"
                      value={registerForm.fullName} onChange={handleRegisterChange}
                      placeholder="Enter teacher names" error={errors.fullName} />
                    <FormInput label="School Name" name="schoolName"
                      value={registerForm.schoolName} onChange={handleRegisterChange}
                      placeholder="Enter school name" error={errors.schoolName} />
                  </>
                )}
                <FormInput label="Email Address" name="email" type="email"
                  value={mode === "login" ? loginForm.email : registerForm.email}
                  onChange={mode === "login" ? handleLoginChange : handleRegisterChange}
                  placeholder="teacher@school.rw" error={errors.email} />
                <FormInput label="Password" name="password" type="password"
                  value={mode === "login" ? loginForm.password : registerForm.password}
                  onChange={mode === "login" ? handleLoginChange : handleRegisterChange}
                  placeholder="Enter password" error={errors.password} />

                <button type="submit" disabled={loading}
                  className={`w-full rounded-2xl px-5 py-4 text-sm font-semibold transition disabled:opacity-60 ${
                    mode === "login"
                      ? "bg-blue-700 text-white hover:bg-blue-800"
                      : "bg-emerald-700 text-white hover:bg-emerald-800"
                  }`}>
                  {loading ? "Please wait..." : mode === "login" ? "Login" : "Register Teacher"}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;
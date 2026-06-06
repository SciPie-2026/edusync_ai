// src/pages/LoginPage.jsx
// Props: onLogin(role) — called with "superadmin" | "collegeadmin" | "faculty"

import { useState } from "react";

export default function LoginPage({ onLogin }) {
  const [form, setForm] = useState({ email: "", password: "", role: "superadmin" });
  const set = key => e => setForm(f => ({ ...f, [key]: e.target.value }));

  return (
    <div className="login-wrap">
      <div className="login-glow" />
      <div className="login-card">
        <div className="login-logo">edusync<span>_ai</span></div>
        <div className="login-sub">AI-Powered Attendance Management</div>

        <h2>Sign in</h2>

        <div className="field">
          <label>Email address</label>
          <input type="email" placeholder="admin@college.edu" value={form.email} onChange={set("email")} />
        </div>
        <div className="field">
          <label>Password</label>
          <input type="password" placeholder="••••••••" value={form.password} onChange={set("password")} />
        </div>
        <div className="field">
          <label>Role</label>
          <select value={form.role} onChange={set("role")}>
            <option value="superadmin">Super Admin</option>
            <option value="collegeadmin">College Admin</option>
            <option value="faculty">Faculty</option>
          </select>
        </div>

        <button
          className="btn btn-primary btn-full"
          style={{ marginTop: 8 }}
          onClick={() => onLogin(form.role)}
        >
          Sign In
        </button>
      </div>
    </div>
  );
}

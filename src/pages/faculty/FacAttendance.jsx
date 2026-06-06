// src/pages/faculty/FacAttendance.jsx
// ★ Most important page ★
// Shows scan columns (Scan 1/2/3), final status badge, per-student override toggle, Export CSV

import { useState } from "react";
import StatusBadge from "../../components/StatusBadge";
import Icon from "../../components/Icon";
import { dummyStudents } from "../../data/dummy";

// Show only SEC A students for this session — swap filter when wiring real API
const SESSION_STUDENTS = dummyStudents.filter(s => s.batch.includes("SEC A"));

export default function FacAttendance({ session, setPage }) {
  const [overrides, setOverrides] = useState({}); // { studentId: true | false }

  const toggleOverride = id =>
    setOverrides(o => ({ ...o, [id]: !( o[id] !== undefined ? o[id] : getAutoStatus(id) === "present") }));

  const getAutoStatus = id => {
    const s = SESSION_STUDENTS.find(s => s.id === id);
    return s && s.scans.filter(Boolean).length >= 2 ? "present" : "absent";
  };

  const getFinalStatus = id =>
    overrides[id] !== undefined
      ? (overrides[id] ? "present" : "absent")
      : getAutoStatus(id);

  const presentCount = SESSION_STUDENTS.filter(s => getFinalStatus(s.id) === "present").length;
  const pct          = Math.round((presentCount / SESSION_STUDENTS.length) * 100);

  return (
    <div className="page">
      {/* ── Session info header ── */}
      <div className="att-header">
        <div className="att-header-top">
          <div>
            <button className="btn btn-ghost" style={{ marginBottom: 10 }} onClick={() => setPage("fac-home")}>
              <Icon name="back" size={13} /> Back
            </button>
            <div className="att-session-title">{session?.subject ?? "Data Structures"}</div>
          </div>
          <button className="btn btn-primary">
            <Icon name="download" size={13} /> Export CSV
          </button>
        </div>

        <div className="att-meta">
          <div className="att-meta-item"><Icon name="students" size={13} />{session?.batch ?? "B.Tech FSD SEC A"}</div>
          <div className="att-meta-item"><Icon name="rooms"    size={13} />{session?.room  ?? "A109"}</div>
          <div className="att-meta-item"><Icon name="sessions" size={13} />{session?.time  ?? "10:00 AM"} · Tue 3 Jun 2025</div>
        </div>
      </div>

      {/* ── Stats bar ── */}
      <div className="att-stats">
        {[
          ["Total",      SESSION_STUDENTS.length,                          "#6c63ff"],
          ["Present",    presentCount,                                     "#22c55e"],
          ["Absent",     SESSION_STUDENTS.length - presentCount,           "#ef4444"],
          ["Percentage", `${pct}%`,  pct >= 75 ? "#22c55e" : "#ef4444"],
        ].map(([label, num, color]) => (
          <div key={label} className="att-stat">
            <div className="att-stat-num" style={{ color }}>{num}</div>
            <div className="att-stat-label">{label}</div>
          </div>
        ))}
      </div>

      {/* ── Attendance table ── */}
      <div className="table-wrap">
        <div className="table-header"><div className="table-title">Student Attendance</div></div>
        <table>
          <thead>
            <tr>
              <th>Roll No.</th>
              <th>Name</th>
              <th style={{ textAlign: "center" }}>Scan 1</th>
              <th style={{ textAlign: "center" }}>Scan 2</th>
              <th style={{ textAlign: "center" }}>Scan 3</th>
              <th>Final Status</th>
              <th>Override</th>
            </tr>
          </thead>
          <tbody>
            {SESSION_STUDENTS.map(s => (
              <tr key={s.id}>
                <td><span style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{s.roll}</span></td>
                <td><strong>{s.name}</strong></td>

                {s.scans.map((hit, i) => (
                  <td key={i} style={{ textAlign: "center" }}>
                    <span className={`scan-dot ${hit ? "yes" : "no"}`}>{hit ? "✓" : "✗"}</span>
                  </td>
                ))}

                <td><StatusBadge status={getFinalStatus(s.id)} /></td>

                <td>
                  <label className="toggle">
                    <input
                      type="checkbox"
                      checked={overrides[s.id] !== undefined ? overrides[s.id] : getFinalStatus(s.id) === "present"}
                      onChange={() => toggleOverride(s.id)}
                    />
                    <span className="toggle-slider" />
                  </label>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

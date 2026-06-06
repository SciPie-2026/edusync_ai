// src/pages/faculty/FacAlerts.jsx
// Shortage alerts — students below 75% attendance, with progress bars + batch filter

import { useState } from "react";
import StatsCard from "../../components/StatsCard";
import { dummyStudents } from "../../data/dummy";

export default function FacAlerts() {
  const [batch, setBatch] = useState("all");
  const batches  = [...new Set(dummyStudents.map(s => s.batch))];
  const filtered = dummyStudents.filter(s => batch === "all" || s.batch === batch);

  const selectStyle = {
    background: "var(--surface2)", border: "1px solid var(--border2)",
    borderRadius: 8, padding: "7px 12px", color: "var(--text)",
    fontFamily: "var(--font)", fontSize: 13, outline: "none",
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Shortage Alerts</div>
        <select style={selectStyle} value={batch} onChange={e => setBatch(e.target.value)}>
          <option value="all">All Batches</option>
          {batches.map(b => <option key={b} value={b}>{b}</option>)}
        </select>
      </div>

      <div className="stats-grid">
        <StatsCard icon="alerts"   num={dummyStudents.filter(s => s.attendance < 75).length} label="Below 75%"     color="#ef4444" />
        <StatsCard icon="students" num={dummyStudents.length}                                label="Total Students" color="#6c63ff" />
        <StatsCard icon="check"    num={dummyStudents.filter(s => s.attendance >= 75).length} label="Safe"           color="#22c55e" />
      </div>

      <div className="table-wrap">
        <div className="table-header"><div className="table-title">Attendance Shortage</div></div>
        <table>
          <thead>
            <tr>
              <th>Student</th><th>Roll No.</th><th>Batch</th>
              <th>Attended / Total</th><th>Attendance %</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(s => (
              <tr key={s.id} className={s.attendance < 75 ? "shortage-row" : ""}>
                <td><strong>{s.name}</strong></td>
                <td><span style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{s.roll}</span></td>
                <td style={{ fontSize: 12, color: "var(--text2)" }}>{s.batch}</td>
                <td>{s.attended}/{s.total}</td>
                <td>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div className="progress-bar" style={{ width: 80 }}>
                      <div
                        className="progress-fill"
                        style={{
                          width: `${s.attendance}%`,
                          background: s.attendance < 75 ? "var(--red)" : "var(--green)",
                        }}
                      />
                    </div>
                    <span style={{
                      fontFamily: "var(--font-mono)", fontWeight: 700, fontSize: 13,
                      color: s.attendance < 75 ? "var(--red)" : "var(--green)",
                    }}>
                      {s.attendance}%
                    </span>
                    {s.attendance < 75 && (
                      <span className="badge badge-red" style={{ fontSize: 10 }}>⚠ Shortage</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

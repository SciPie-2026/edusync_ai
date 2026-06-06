// src/pages/collegeadmin/CAHome.jsx
// College Admin — overview stats + recent sessions + shortage snapshot

import StatsCard from "../../components/StatsCard";
import StatusBadge from "../../components/StatusBadge";
import { dummySessions, dummyStudents } from "../../data/dummy";

export default function CAHome() {
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">College Dashboard</div>
      </div>

      <div className="stats-grid">
        <StatsCard icon="students" num="2,340" label="Total Students"    color="#3b82f6" />
        <StatsCard icon="rooms"    num="18"    label="Active Rooms"       color="#22c55e" />
        <StatsCard icon="sessions" num="34"    label="Sessions Today"     color="#f59e0b" />
        <StatsCard icon="check"    num="1,820" label="Attendance Today"   color="#6c63ff" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        {/* Recent sessions */}
        <div className="table-wrap">
          <div className="table-header"><div className="table-title">Recent Sessions</div></div>
          <table>
            <thead><tr><th>Subject</th><th>Room</th><th>Status</th></tr></thead>
            <tbody>
              {dummySessions.slice(0, 4).map(s => (
                <tr key={s.id}>
                  <td>
                    <strong>{s.subject}</strong><br />
                    <span style={{ color: "var(--text2)", fontSize: 11 }}>{s.batch}</span>
                  </td>
                  <td><span className="tag">{s.room}</span></td>
                  <td><StatusBadge status={s.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Shortage alerts */}
        <div className="table-wrap">
          <div className="table-header"><div className="table-title">Shortage Alerts</div></div>
          <table>
            <thead><tr><th>Student</th><th>Attendance</th></tr></thead>
            <tbody>
              {dummyStudents.filter(s => s.attendance < 75).map(s => (
                <tr key={s.id}>
                  <td>{s.name}</td>
                  <td>
                    <span style={{ color: "var(--red)", fontWeight: 700 }}>
                      {s.attendance}%
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

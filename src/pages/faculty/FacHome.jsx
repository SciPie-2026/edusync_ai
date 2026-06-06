// src/pages/faculty/FacHome.jsx
// Faculty — today's session cards; click to open attendance

import StatsCard from "../../components/StatsCard";
import StatusBadge from "../../components/StatusBadge";
import Icon from "../../components/Icon";
import { dummySessions } from "../../data/dummy";

// Filter to only Dr. Sharma's sessions — swap this when wiring real auth
const MY_SESSIONS = dummySessions.filter(s => s.faculty === "Dr. Sharma");

export default function FacHome({ setPage, setActiveSession }) {
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Today's Sessions</div>
      </div>

      <div className="stats-grid">
        <StatsCard icon="sessions" num={MY_SESSIONS.length}                                    label="Total Sessions" color="#6c63ff" />
        <StatsCard icon="check"    num={MY_SESSIONS.filter(s => s.status === "done").length}    label="Completed"      color="#22c55e" />
        <StatsCard icon="alerts"   num={MY_SESSIONS.filter(s => s.status === "pending").length} label="Pending"        color="#f59e0b" />
      </div>

      <div className="session-grid">
        {MY_SESSIONS.map(s => (
          <div
            key={s.id}
            className="session-card"
            onClick={() => { setActiveSession(s); setPage("fac-attendance"); }}
          >
            <div className="session-card-top">
              <div>
                <div className="session-subject">{s.subject}</div>
                <div className="session-meta">{s.batch}</div>
              </div>
              <StatusBadge status={s.status} />
            </div>

            <div style={{ display: "flex", gap: 12, marginTop: 8 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: "var(--text2)" }}>
                <Icon name="rooms"    size={12} /> {s.room}
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: "var(--text2)" }}>
                <Icon name="sessions" size={12} /> {s.time}
              </div>
            </div>

            <div className="session-footer">
              <span style={{ fontSize: 12, color: "var(--text3)" }}>{s.duration} min</span>
              <span style={{ fontSize: 12, color: "var(--accent2)" }}>View Attendance →</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

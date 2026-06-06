// src/pages/collegeadmin/CATimetable.jsx
// Read-only weekly timetable grid (Mon–Sat, 09:00–16:00)

import { timetable } from "../../data/dummy";

const DAYS  = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const TIMES = ["09:00","10:00","11:00","12:00","13:00","14:00","15:00","16:00"];

export default function CATimetable() {
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Timetable</div>
        <span className="badge badge-purple">Read Only — Synced from DB</span>
      </div>

      <div className="tt-wrap">
        <div className="tt-grid">
          {/* Header row */}
          <div className="tt-header">Time</div>
          {DAYS.map(d => <div key={d} className="tt-header">{d}</div>)}

          {/* Time rows */}
          {TIMES.map(t => (
            <>
              <div key={t + "-label"} className="tt-time">{t}</div>
              {DAYS.map(d => {
                const slot = (timetable[d] || []).find(s => s.time === t);
                return (
                  <div key={d + t} className="tt-cell">
                    {slot && (
                      <div className="tt-slot">
                        <div className="tt-slot-subject">{slot.subject}</div>
                        <div className="tt-slot-meta">{slot.batch} · {slot.room}</div>
                        <div className="tt-slot-meta">{slot.faculty}</div>
                      </div>
                    )}
                  </div>
                );
              })}
            </>
          ))}
        </div>
      </div>
    </div>
  );
}

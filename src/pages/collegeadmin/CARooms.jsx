// src/pages/collegeadmin/CARooms.jsx
// Rooms & Cameras — list + Add Room modal

import { useState } from "react";
import StatusBadge from "../../components/StatusBadge";
import Icon from "../../components/Icon";
import { dummyRooms } from "../../data/dummy";

export default function CARooms() {
  const [showAdd, setShowAdd] = useState(false);
  const [form, setForm] = useState({ number: "", rtsp: "", label: "" });
  const set = key => e => setForm(f => ({ ...f, [key]: e.target.value }));

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Rooms & Cameras</div>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
          <Icon name="plus" size={13} /> Add Room
        </button>
      </div>

      <div className="table-wrap">
        <div className="table-header"><div className="table-title">Room Registry</div></div>
        <table>
          <thead>
            <tr>
              <th>Room No.</th><th>RTSP URL</th><th>Label</th>
              <th>Camera Status</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {dummyRooms.map(r => (
              <tr key={r.id}>
                <td><strong style={{ fontFamily: "var(--font-mono)" }}>{r.number}</strong></td>
                <td><span className="tag">{r.rtsp}</span></td>
                <td style={{ color: "var(--text2)" }}>{r.label || "—"}</td>
                <td><StatusBadge status={r.status} /></td>
                <td>
                  <div className="actions">
                    <button className="btn btn-ghost"><Icon name="eye"   size={12} /> View</button>
                    <button className="btn btn-danger"><Icon name="trash" size={12} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Add Room Modal ── */}
      {showAdd && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setShowAdd(false)}>
          <div className="modal">
            <h3>Add Room</h3>

            <div className="field">
              <label>Room Number</label>
              <input placeholder="e.g. A109" value={form.number} onChange={set("number")} />
            </div>
            <div className="field">
              <label>RTSP URL</label>
              <input placeholder="rtsp://10.0.1.9/stream" value={form.rtsp} onChange={set("rtsp")} />
            </div>
            <div className="field">
              <label>Camera Label (optional)</label>
              <input placeholder="Front Camera" value={form.label} onChange={set("label")} />
            </div>

            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary">Save Room</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

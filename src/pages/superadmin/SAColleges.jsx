// src/pages/superadmin/SAColleges.jsx
// Full colleges list + Add College modal with DB config + Test Connection

import { useState } from "react";
import StatsCard from "../../components/StatsCard";
import StatusBadge from "../../components/StatusBadge";
import Icon from "../../components/Icon";
import { dummyColleges } from "../../data/dummy";

export default function SAColleges() {
  const [showAdd,  setShowAdd]  = useState(false);
  const [connTest, setConnTest] = useState(null); // null | "testing" | "success" | "fail"
  const [form, setForm] = useState({
    name: "", city: "", dbType: "MySQL",
    host: "", port: "3306", dbName: "", user: "", pass: "",
  });

  const set = key => e => setForm(f => ({ ...f, [key]: e.target.value }));

  const testConnection = () => {
    setConnTest("testing");
    // Replace with real API call later
    setTimeout(() => setConnTest("success"), 1200);
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Colleges</div>
        <button className="btn btn-primary" onClick={() => setShowAdd(true)}>
          <Icon name="plus" size={13} /> Add College
        </button>
      </div>

      <div className="stats-grid">
        <StatsCard icon="college" num="24" label="Total Colleges" color="#6c63ff" />
        <StatsCard icon="check"   num="21" label="Synced"          color="#22c55e" />
        <StatsCard icon="alerts"  num="3"  label="Errors"          color="#ef4444" />
      </div>

      <div className="table-wrap">
        <div className="table-header"><div className="table-title">All Colleges</div></div>
        <table>
          <thead>
            <tr>
              <th>Name</th><th>City</th><th>DB Type</th>
              <th>Sync Status</th><th>Last Synced</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {dummyColleges.map(c => (
              <tr key={c.id}>
                <td><strong>{c.name}</strong></td>
                <td>{c.city}</td>
                <td><span className="tag">{c.dbType}</span></td>
                <td><StatusBadge status={c.syncStatus} /></td>
                <td style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text2)" }}>
                  {c.lastSynced}
                </td>
                <td>
                  <div className="actions">
                    <button className="btn btn-ghost"><Icon name="eye"   size={12} /> View</button>
                    <button className="btn btn-ghost"><Icon name="sync"  size={12} /> Sync Now</button>
                    <button className="btn btn-danger"><Icon name="trash" size={12} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── Add College Modal ── */}
      {showAdd && (
        <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setShowAdd(false)}>
          <div className="modal">
            <h3>Add New College</h3>

            <div className="inline-fields">
              <div className="field">
                <label>College Name</label>
                <input placeholder="e.g. IIT Bombay" value={form.name} onChange={set("name")} />
              </div>
              <div className="field">
                <label>City</label>
                <input placeholder="Mumbai" value={form.city} onChange={set("city")} />
              </div>
            </div>

            <div className="field">
              <label>Database Type</label>
              <select value={form.dbType} onChange={set("dbType")}>
                <option>MySQL</option>
                <option>PostgreSQL</option>
              </select>
            </div>

            <div className="inline-fields">
              <div className="field">
                <label>DB Host</label>
                <input placeholder="10.0.0.1" value={form.host} onChange={set("host")} />
              </div>
              <div className="field">
                <label>Port</label>
                <input placeholder="3306" value={form.port} onChange={set("port")} />
              </div>
            </div>

            <div className="field">
              <label>Database Name</label>
              <input placeholder="college_db" value={form.dbName} onChange={set("dbName")} />
            </div>

            <div className="inline-fields">
              <div className="field">
                <label>Username</label>
                <input placeholder="db_user" value={form.user} onChange={set("user")} />
              </div>
              <div className="field">
                <label>Password</label>
                <input type="password" placeholder="••••••" value={form.pass} onChange={set("pass")} />
              </div>
            </div>

            <div className="conn-test">
              <button className="btn btn-ghost" onClick={testConnection}>
                <Icon name="sync" size={12} /> Test Connection
              </button>
              {connTest === "testing" && (
                <span style={{ color: "var(--text2)", fontSize: 13 }}>Testing…</span>
              )}
              {connTest === "success" && (
                <span style={{ color: "var(--green)", fontSize: 13 }}>✓ Connection successful</span>
              )}
              {connTest === "fail" && (
                <span style={{ color: "var(--red)", fontSize: 13 }}>✗ Connection failed</span>
              )}
            </div>

            <div className="modal-footer">
              <button className="btn btn-ghost" onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary">Save College</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

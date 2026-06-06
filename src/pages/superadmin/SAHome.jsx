// src/pages/superadmin/SAHome.jsx
// Super Admin — platform overview + college list snapshot

import StatsCard from "../../components/StatsCard";
import StatusBadge from "../../components/StatusBadge";
import Icon from "../../components/Icon";
import { dummyColleges } from "../../data/dummy";

export default function SAHome({ setPage }) {
  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Platform Overview</div>
      </div>

      <div className="stats-grid">
        <StatsCard icon="college"  num="24"     label="Total Colleges"      color="#6c63ff" />
        <StatsCard icon="students" num="18,430" label="Total Students"       color="#3b82f6" />
        <StatsCard icon="sessions" num="142"    label="Sessions Today"       color="#f59e0b" />
        <StatsCard icon="check"    num="12,890" label="Attendance Marked"    color="#22c55e" />
      </div>

      <div className="table-wrap">
        <div className="table-header">
          <div className="table-title">College Tenants</div>
          <button className="btn btn-primary" onClick={() => setPage("sa-colleges")}>
            <Icon name="plus" size={13} /> Add College
          </button>
        </div>
        <table>
          <thead>
            <tr>
              <th>College</th>
              <th>City</th>
              <th>DB Status</th>
              <th>Last Synced</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {dummyColleges.map(c => (
              <tr key={c.id}>
                <td><strong>{c.name}</strong></td>
                <td>{c.city}</td>
                <td><StatusBadge status={c.syncStatus} /></td>
                <td style={{ fontFamily: "var(--font-mono)", fontSize: 12, color: "var(--text2)" }}>
                  {c.lastSynced}
                </td>
                <td>
                  <div className="actions">
                    <button className="btn btn-ghost"><Icon name="eye"   size={12} /> View</button>
                    <button className="btn btn-ghost"><Icon name="sync"  size={12} /> Sync</button>
                    <button className="btn btn-danger"><Icon name="trash" size={12} /></button>
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

// src/pages/collegeadmin/CAStudents.jsx
// Students list with search + batch filter + photo upload per row

import { useState } from "react";
import StatusBadge from "../../components/StatusBadge";
import Icon from "../../components/Icon";
import { dummyStudents } from "../../data/dummy";

export default function CAStudents() {
  const [search, setSearch] = useState("");
  const [batch,  setBatch]  = useState("all");

  const batches  = [...new Set(dummyStudents.map(s => s.batch))];
  const filtered = dummyStudents.filter(s =>
    (batch === "all" || s.batch === batch) &&
    (s.name.toLowerCase().includes(search.toLowerCase()) || s.roll.includes(search))
  );

  const selectStyle = {
    background: "var(--surface2)", border: "1px solid var(--border2)",
    borderRadius: 8, padding: "7px 12px", color: "var(--text)",
    fontFamily: "var(--font)", fontSize: 13, outline: "none",
  };

  return (
    <div className="page">
      <div className="page-header">
        <div className="page-title">Students</div>
      </div>

      <div className="table-wrap">
        <div className="table-header">
          <div className="table-title">Student Registry</div>
          <div style={{ display: "flex", gap: 10 }}>
            <div className="search-bar">
              <Icon name="search" size={14} color="var(--text3)" />
              <input
                placeholder="Name or roll no."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <select style={selectStyle} value={batch} onChange={e => setBatch(e.target.value)}>
              <option value="all">All Batches</option>
              {batches.map(b => <option key={b} value={b}>{b}</option>)}
            </select>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Roll No.</th><th>Name</th><th>Batch</th>
              <th>Photo</th><th>Embedding</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map(s => (
              <tr key={s.id}>
                <td><span style={{ fontFamily: "var(--font-mono)", fontSize: 12 }}>{s.roll}</span></td>
                <td><strong>{s.name}</strong></td>
                <td style={{ color: "var(--text2)", fontSize: 12 }}>{s.batch}</td>
                <td>
                  <div style={{
                    width: 32, height: 32, borderRadius: 8,
                    background: "var(--surface2)", border: "1px solid var(--border)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                  }}>
                    <Icon name="students" size={14} color="var(--text3)" />
                  </div>
                </td>
                <td><StatusBadge status={s.embeddingStatus} /></td>
                <td>
                  <button className="btn btn-ghost">
                    <Icon name="camera" size={12} /> Upload Photo
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

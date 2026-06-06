// src/components/TopBar.jsx
// Props: title (string), collegeName (string), userName (string)

export default function TopBar({ title, collegeName, userName }) {
  return (
    <div className="topbar">
      <div className="topbar-title">{title}</div>
      <span style={{ color: "var(--text3)", fontSize: 12 }}>{collegeName}</span>
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <div className="avatar" style={{ width: 28, height: 28, fontSize: 11 }}>
          {userName?.[0] ?? "U"}
        </div>
        <span style={{ fontSize: 13, color: "var(--text2)" }}>{userName}</span>
      </div>
    </div>
  );
}

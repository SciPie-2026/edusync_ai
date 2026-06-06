// src/components/StatsCard.jsx
// Usage: <StatsCard icon="students" num="2,340" label="Total Students" color="#3b82f6" />

import Icon from "./Icon";

export default function StatsCard({ icon, num, label, color = "#6c63ff" }) {
  return (
    <div className="stat-card">
      <div className="stat-icon" style={{ background: `${color}18` }}>
        <Icon name={icon} size={20} color={color} />
      </div>
      <div>
        <div className="stat-num">{num}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}

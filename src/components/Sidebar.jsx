// src/components/Sidebar.jsx
// Props: role ("superadmin" | "collegeadmin" | "faculty"), page, setPage, onLogout

import Icon from "./Icon";

const NAV_LINKS = {
  superadmin: [
    { label: "Overview",  key: "sa-home",     icon: "dashboard" },
    { label: "Colleges",  key: "sa-colleges",  icon: "college"   },
  ],
  collegeadmin: [
    { label: "Overview",   key: "ca-home",      icon: "dashboard" },
    { label: "Rooms",      key: "ca-rooms",     icon: "rooms"     },
    { label: "Students",   key: "ca-students",  icon: "students"  },
    { label: "Timetable",  key: "ca-timetable", icon: "timetable" },
  ],
  faculty: [
    { label: "Today's Sessions", key: "fac-home",   icon: "sessions" },
    { label: "Shortage Alerts",  key: "fac-alerts", icon: "alerts"   },
  ],
};

const ROLE_LABELS = {
  superadmin:   "Super Admin",
  collegeadmin: "College Admin",
  faculty:      "Faculty",
};

const USER_NAMES = {
  superadmin:   "Root Admin",
  collegeadmin: "Dr. Sharma",
  faculty:      "Dr. Sharma",
};

export default function Sidebar({ role, page, setPage, onLogout }) {
  const links    = NAV_LINKS[role] || [];
  const roleName = ROLE_LABELS[role];
  const userName = USER_NAMES[role];

  return (
    <div className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-text">edusync<span>_ai</span></div>
        <div className="sidebar-role">{roleName}</div>
      </div>

      {/* Nav links */}
      <div className="sidebar-nav">
        {links.map(n => (
          <div
            key={n.key}
            className={`nav-item ${page === n.key ? "active" : ""}`}
            onClick={() => setPage(n.key)}
          >
            <Icon name={n.icon} size={15} />
            {n.label}
          </div>
        ))}
      </div>

      {/* Footer: user + logout */}
      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="avatar">{userName[0]}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{userName}</div>
            <div style={{ fontSize: 11, color: "var(--text3)" }}>{roleName}</div>
          </div>
        </div>
        <div
          className="nav-item"
          style={{ marginTop: 6, color: "var(--red)", opacity: 0.8 }}
          onClick={onLogout}
        >
          <Icon name="logout" size={14} />
          Sign Out
        </div>
      </div>
    </div>
  );
}

// src/App.jsx
// Root component — handles auth state, routing, sidebar + topbar wiring

import { useState } from "react";
import "./styles/global.css";

// Shared components
import Sidebar  from "./components/Sidebar";
import TopBar   from "./components/TopBar";

// Pages
import LoginPage     from "./pages/LoginPage";
import SAHome        from "./pages/superadmin/SAHome";
import SAColleges    from "./pages/superadmin/SAColleges";
import CAHome        from "./pages/collegeadmin/CAHome";
import CARooms       from "./pages/collegeadmin/CARooms";
import CAStudents    from "./pages/collegeadmin/CAStudents";
import CATimetable   from "./pages/collegeadmin/CATimetable";
import FacHome       from "./pages/faculty/FacHome";
import FacAttendance from "./pages/faculty/FacAttendance";
import FacAlerts     from "./pages/faculty/FacAlerts";

// ── Config maps ────────────────────────────────────────────────────────────────
const DEFAULT_PAGE = {
  superadmin:   "sa-home",
  collegeadmin: "ca-home",
  faculty:      "fac-home",
};

const TOPBAR_TITLES = {
  "sa-home":       "Platform Overview",
  "sa-colleges":   "Colleges",
  "ca-home":       "Dashboard",
  "ca-rooms":      "Rooms & Cameras",
  "ca-students":   "Students",
  "ca-timetable":  "Timetable",
  "fac-home":      "Today's Sessions",
  "fac-attendance":"Session Attendance",
  "fac-alerts":    "Shortage Alerts",
};

const COLLEGE_NAMES = {
  superadmin:   "Platform",
  collegeadmin: "IIT Delhi",
  faculty:      "IIT Delhi",
};

const USER_NAMES = {
  superadmin:   "Root Admin",
  collegeadmin: "Dr. Sharma",
  faculty:      "Dr. Sharma",
};

// ── App ────────────────────────────────────────────────────────────────────────
export default function App() {
  const [role,          setRole]          = useState(null);
  const [page,          setPage]          = useState(null);
  const [activeSession, setActiveSession] = useState(null);

  const handleLogin = (selectedRole) => {
    setRole(selectedRole);
    setPage(DEFAULT_PAGE[selectedRole]);
  };

  const handleLogout = () => {
    setRole(null);
    setPage(null);
  };

  // Page renderer — add new pages here
  const renderPage = () => {
    switch (page) {
      // Super Admin
      case "sa-home":       return <SAHome setPage={setPage} />;
      case "sa-colleges":   return <SAColleges />;
      // College Admin
      case "ca-home":       return <CAHome />;
      case "ca-rooms":      return <CARooms />;
      case "ca-students":   return <CAStudents />;
      case "ca-timetable":  return <CATimetable />;
      // Faculty
      case "fac-home":      return <FacHome setPage={setPage} setActiveSession={setActiveSession} />;
      case "fac-attendance":return <FacAttendance session={activeSession} setPage={setPage} />;
      case "fac-alerts":    return <FacAlerts />;
      default:              return null;
    }
  };

  if (!role) return <LoginPage onLogin={handleLogin} />;

  return (
    <div className="app-layout">
      <Sidebar
        role={role}
        page={page}
        setPage={setPage}
        onLogout={handleLogout}
      />
      <div className="main">
        <TopBar
          title={TOPBAR_TITLES[page]}
          collegeName={COLLEGE_NAMES[role]}
          userName={USER_NAMES[role]}
        />
        {renderPage()}
      </div>
    </div>
  );
}

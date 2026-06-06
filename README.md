# edusync_ai — File Structure Guide

## Folder Structure

```
src/
│
├── App.jsx                          ← Root. Handles login state + page routing
│
├── styles/
│   └── global.css                   ← All CSS variables, layout, tables, badges, etc.
│                                      Import this ONCE in App.jsx or main.jsx
│
├── data/
│   └── dummy.js                     ← Fake data for all pages. Replace exports
│                                      with real API calls when backend is ready.
│
├── components/                      ← Reusable pieces used across all pages
│   ├── Icon.jsx                     ← SVG icon set. Usage: <Icon name="rooms" size={16} />
│   ├── StatusBadge.jsx              ← Colored pill. Usage: <StatusBadge status="present" />
│   ├── StatsCard.jsx                ← Stat tile. Usage: <StatsCard icon="students" num="2,340" label="..." />
│   ├── Sidebar.jsx                  ← Role-aware nav sidebar
│   └── TopBar.jsx                   ← Top bar with page title + user info
│
├── pages/
│   ├── LoginPage.jsx                ← Email + password + role dropdown
│   │
│   ├── superadmin/
│   │   ├── SAHome.jsx               ← Platform stats + college list
│   │   └── SAColleges.jsx           ← Full colleges table + Add College modal
│   │
│   ├── collegeadmin/
│   │   ├── CAHome.jsx               ← College stats + session/shortage snapshots
│   │   ├── CARooms.jsx              ← Rooms table + Add Room modal
│   │   ├── CAStudents.jsx           ← Students table with search + batch filter
│   │   └── CATimetable.jsx          ← Read-only weekly grid
│   │
│   └── faculty/
│       ├── FacHome.jsx              ← Session cards for today
│       ├── FacAttendance.jsx        ← ★ Core page — scan columns, override toggle, export
│       └── FacAlerts.jsx            ← Shortage alerts table with progress bars
```

---

## How to plug it in

### 1. Copy files
Drop the entire `src/` folder into your React project (Vite / CRA both work).

### 2. Import global CSS
In your `main.jsx` (or `index.jsx`):
```jsx
import "./styles/global.css";
```
Remove that same import from `App.jsx` if you add it to `main.jsx` — pick one.

### 3. Render App
```jsx
// main.jsx
import React from "react";
import ReactDOM from "react-dom/client";
import "./styles/global.css";
import App from "./App";

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
```

### 4. Add a Google Fonts link (for the custom fonts)
In your `index.html` `<head>`:
```html
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
```

---

## Wiring real API data

When your backend is ready, just swap out imports in each page:

```js
// BEFORE (dummy)
import { dummyStudents } from "../../data/dummy";

// AFTER (real API)
const [students, setStudents] = useState([]);
useEffect(() => {
  fetch("/api/students").then(r => r.json()).then(setStudents);
}, []);
```

Each page is isolated — swapping one doesn't affect others.

---

## Adding a new page

1. Create `src/pages/<role>/NewPage.jsx`
2. Import it in `App.jsx`
3. Add a `case "new-page-key": return <NewPage />;` to the switch
4. Add `{ label: "New Page", key: "new-page-key", icon: "..." }` to `NAV_LINKS` in `Sidebar.jsx`
5. Add `"new-page-key": "Page Title"` to `TOPBAR_TITLES` in `App.jsx`

---

## Key files to touch first

| Task                         | File                                    |
|------------------------------|-----------------------------------------|
| Change colors / fonts        | `src/styles/global.css` → `:root {}`   |
| Add/remove nav links         | `src/components/Sidebar.jsx`            |
| Change dummy data            | `src/data/dummy.js`                     |
| Wire session attendance API  | `src/pages/faculty/FacAttendance.jsx`   |
| Wire login to real auth      | `src/pages/LoginPage.jsx` + `App.jsx`   |

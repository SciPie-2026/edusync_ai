// src/components/Icon.jsx
// Usage: <Icon name="dashboard" size={16} color="#fff" />

const icons = {
  dashboard: <><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></>,
  college:   <><path d="M12 3L2 8l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></>,
  sessions:  <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 2v2M16 2v2M3 10h18"/></>,
  students:  <><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></>,
  rooms:     <><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 3v18M3 9h18"/></>,
  timetable: <><rect x="3" y="4" width="18" height="16" rx="2"/><path d="M8 2v2M16 2v2M3 10h18M8 15h4M8 18h2"/></>,
  alerts:    <><path d="M10.3 3.5L2 19h20L13.7 3.5a2 2 0 00-3.4 0z"/><path d="M12 9v4M12 17h.01"/></>,
  logout:    <><path d="M17 16l4-4-4-4"/><path d="M21 12H9M9 7H5a2 2 0 00-2 2v6a2 2 0 002 2h4"/></>,
  search:    <><circle cx="11" cy="11" r="7"/><path d="m21 21-4.35-4.35"/></>,
  plus:      <><path d="M12 5v14M5 12h14"/></>,
  sync:      <><path d="M21 12a9 9 0 11-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/></>,
  trash:     <><path d="M3 6h18M8 6V4h8v2M19 6l-1 14H6L5 6"/></>,
  eye:       <><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></>,
  download:  <><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/></>,
  back:      <><path d="M19 12H5M12 5l-7 7 7 7"/></>,
  camera:    <><path d="M23 19a2 2 0 01-2 2H3a2 2 0 01-2-2V8a2 2 0 012-2h4l2-3h6l2 3h4a2 2 0 012 2z"/><circle cx="12" cy="13" r="4"/></>,
  check:     <><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h11"/></>,
};

export default function Icon({ name, size = 16, color }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke={color || "currentColor"}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {icons[name] || null}
    </svg>
  );
}

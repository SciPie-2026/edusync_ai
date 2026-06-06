// src/components/StatusBadge.jsx
// Usage: <StatusBadge status="present" />
// Accepted values: present, absent, pending, done, synced, syncing, error,
//                  active, offline, registered, "not registered"

export default function StatusBadge({ status }) {
  const map = {
    present:          ["badge-green",  "Present"],
    absent:           ["badge-red",    "Absent"],
    pending:          ["badge-yellow", "Pending"],
    done:             ["badge-green",  "Done"],
    synced:           ["badge-green",  "Synced"],
    syncing:          ["badge-yellow", "Syncing"],
    error:            ["badge-red",    "Error"],
    active:           ["badge-green",  "Active"],
    offline:          ["badge-red",    "Offline"],
    registered:       ["badge-blue",   "Registered"],
    "not registered": ["badge-red",    "Not Registered"],
  };

  const [cls, label] = map[status] || ["badge-purple", status];
  return <span className={`badge ${cls}`}>{label}</span>;
}

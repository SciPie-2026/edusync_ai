export const dummySessions = [
  { id: "s001", subject: "Data Structures", batch: "B.Tech FSD SEC A", room: "A109", time: "10:00 AM", duration: 60, status: "done", faculty: "Dr. Sharma" },
  { id: "s002", subject: "DBMS", batch: "B.Tech FSD SEC A", room: "B204", time: "11:00 AM", duration: 60, status: "pending", faculty: "Dr. Mehta" },
  { id: "s003", subject: "OS", batch: "B.Tech FSD SEC B", room: "C301", time: "12:00 PM", duration: 60, status: "done", faculty: "Dr. Sharma" },
  { id: "s004", subject: "CN", batch: "B.Tech FSD SEC A", room: "A109", time: "02:00 PM", duration: 60, status: "pending", faculty: "Dr. Sharma" },
];

export const dummyStudents = [
  { id: "STU001", roll: "22CSE001", name: "Anant Kumar", batch: "B.Tech FSD SEC A", embeddingStatus: "registered", photo: null, attendance: 82, attended: 41, total: 50, scans: [true, true, true] },
  { id: "STU002", roll: "22CSE002", name: "Rohan Vashisth", batch: "B.Tech FSD SEC A", embeddingStatus: "registered", photo: null, attendance: 68, attended: 34, total: 50, scans: [false, false, false] },
  { id: "STU003", roll: "22CSE003", name: "Yug Verma", batch: "B.Tech FSD SEC A", embeddingStatus: "not registered", photo: null, attendance: 74, attended: 37, total: 50, scans: [true, true, false] },
  { id: "STU004", roll: "22CSE004", name: "Vasu Aggarwal", batch: "B.Tech FSD SEC A", embeddingStatus: "registered", photo: null, attendance: 91, attended: 46, total: 50, scans: [true, true, true] },
  { id: "STU005", roll: "22CSE005", name: "Priya Nair", batch: "B.Tech FSD SEC B", embeddingStatus: "registered", photo: null, attendance: 55, attended: 28, total: 50, scans: [false, true, false] },
  { id: "STU006", roll: "22CSE006", name: "Arjun Singh", batch: "B.Tech FSD SEC B", embeddingStatus: "not registered", photo: null, attendance: 48, attended: 24, total: 50, scans: [false, false, false] },
];

export const dummyColleges = [
  { id: "c001", name: "IIT Delhi", city: "New Delhi", dbType: "MySQL", syncStatus: "synced", lastSynced: "2 min ago" },
  { id: "c002", name: "BITS Pilani", city: "Pilani", dbType: "PostgreSQL", syncStatus: "syncing", lastSynced: "5 min ago" },
  { id: "c003", name: "NIT Trichy", city: "Trichy", dbType: "MySQL", syncStatus: "error", lastSynced: "1 hr ago" },
];

export const dummyRooms = [
  { id: "r001", number: "A109", rtsp: "rtsp://10.0.1.9/stream", label: "Main Cam", status: "active" },
  { id: "r002", number: "B204", rtsp: "rtsp://10.0.2.4/stream", label: "Side Cam", status: "active" },
  { id: "r003", number: "C301", rtsp: "rtsp://10.0.3.1/stream", label: "", status: "offline" },
];

export const timetable = {
  Mon: [
    { time: "10:00", subject: "Data Structures", batch: "SEC A", room: "A109", faculty: "Dr. Sharma" },
    { time: "11:00", subject: "DBMS", batch: "SEC A", room: "B204", faculty: "Dr. Mehta" },
    { time: "14:00", subject: "OS", batch: "SEC B", room: "C301", faculty: "Dr. Kumar" },
  ],
  Tue: [
    { time: "09:00", subject: "CN", batch: "SEC A", room: "A109", faculty: "Dr. Sharma" },
    { time: "13:00", subject: "ML", batch: "SEC B", room: "B204", faculty: "Dr. Nair" },
  ],
  Wed: [
    { time: "10:00", subject: "Data Structures", batch: "SEC B", room: "A109", faculty: "Dr. Sharma" },
    { time: "15:00", subject: "DBMS", batch: "SEC B", room: "C301", faculty: "Dr. Mehta" },
  ],
  Thu: [
    { time: "11:00", subject: "OS", batch: "SEC A", room: "B204", faculty: "Dr. Kumar" },
    { time: "14:00", subject: "CN", batch: "SEC B", room: "A109", faculty: "Dr. Sharma" },
  ],
  Fri: [
    { time: "09:00", subject: "ML", batch: "SEC A", room: "C301", faculty: "Dr. Nair" },
    { time: "12:00", subject: "Data Structures", batch: "SEC A", room: "A109", faculty: "Dr. Sharma" },
  ],
  Sat: [
    { time: "10:00", subject: "Lab - DS", batch: "SEC A", room: "Lab1", faculty: "Dr. Sharma" },
  ],
};

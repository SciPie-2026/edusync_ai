-- ── Tenants ────────────────────────────────────────────────────────────────────
CREATE TABLE tenants (
    id          VARCHAR(20) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    city        VARCHAR(100),
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── Sections / Batches ─────────────────────────────────────────────────────────
CREATE TABLE sections (
    id          SERIAL PRIMARY KEY,
    tenant_id   VARCHAR(20) REFERENCES tenants(id),
    name        VARCHAR(50) NOT NULL,  -- e.g. BT-FSD-A
    program     VARCHAR(50),           -- e.g. B.Tech FSD
    semester    INT,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── Students ───────────────────────────────────────────────────────────────────
CREATE TABLE students (
    id              SERIAL PRIMARY KEY,
    tenant_id       VARCHAR(20) REFERENCES tenants(id),
    roll_no         VARCHAR(20) NOT NULL,
    name            VARCHAR(100) NOT NULL,
    section_id      INT REFERENCES sections(id),
    photo_path      VARCHAR(255),
    embedding_path  VARCHAR(255),
    registered      BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP DEFAULT NOW(),
    UNIQUE(tenant_id, roll_no)
);

-- ── Room Cameras ───────────────────────────────────────────────────────────────
CREATE TABLE room_cameras (
    id          SERIAL PRIMARY KEY,
    tenant_id   VARCHAR(20) REFERENCES tenants(id),
    room_no     VARCHAR(20) NOT NULL,
    rtsp_url    VARCHAR(255) NOT NULL,
    label       VARCHAR(100),
    active      BOOLEAN DEFAULT TRUE,
    UNIQUE(tenant_id, room_no)
);

-- ── Timetable ──────────────────────────────────────────────────────────────────
CREATE TABLE timetable (
    id          SERIAL PRIMARY KEY,
    tenant_id   VARCHAR(20) REFERENCES tenants(id),
    room_no     VARCHAR(20) NOT NULL,
    section_id  INT REFERENCES sections(id),
    subject     VARCHAR(100),
    faculty     VARCHAR(100),
    day_of_week VARCHAR(10) NOT NULL,  -- MON, TUE, WED...
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL
);

-- ── Sessions (one per class that actually ran) ─────────────────────────────────
CREATE TABLE sessions (
    id          SERIAL PRIMARY KEY,
    tenant_id   VARCHAR(20) REFERENCES tenants(id),
    timetable_id INT REFERENCES timetable(id),
    room_no     VARCHAR(20),
    section_id  INT REFERENCES sections(id),
    subject     VARCHAR(100),
    date        DATE NOT NULL,
    start_time  TIME NOT NULL,
    end_time    TIME NOT NULL,
    status      VARCHAR(20) DEFAULT 'scheduled', -- scheduled/running/done
    created_at  TIMESTAMP DEFAULT NOW()
);

-- ── Scans (each of the 3-4 scan triggers per session) ─────────────────────────
CREATE TABLE scans (
    id          SERIAL PRIMARY KEY,
    session_id  INT REFERENCES sessions(id),
    scan_number INT NOT NULL,   -- 1, 2, 3, 4
    triggered_at TIMESTAMP,
    completed_at TIMESTAMP,
    heads_detected INT DEFAULT 0
);

-- ── Attendance ─────────────────────────────────────────────────────────────────
CREATE TABLE attendance (
    id          SERIAL PRIMARY KEY,
    tenant_id   VARCHAR(20) REFERENCES tenants(id),
    session_id  INT REFERENCES sessions(id),
    student_id  INT REFERENCES students(id),
    scan_1      BOOLEAN DEFAULT FALSE,
    scan_2      BOOLEAN DEFAULT FALSE,
    scan_3      BOOLEAN DEFAULT FALSE,
    scan_4      BOOLEAN DEFAULT FALSE,
    final_status VARCHAR(20) DEFAULT 'absent',  -- present/absent/manual
    override    BOOLEAN DEFAULT FALSE,
    override_by VARCHAR(100),
    marked_at   TIMESTAMP DEFAULT NOW()
);
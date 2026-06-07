-- Tenant
INSERT INTO tenants (id, name, city)
VALUES ('TENANT001', 'K.R. Mangalam University', 'Gurugram');

-- Section
INSERT INTO sections (tenant_id, name, program, semester)
VALUES ('TENANT001', 'BT-FSD-A', 'B.Tech FSD', 4);

-- Students (add your actual team + a few extras)
INSERT INTO students (tenant_id, roll_no, name, section_id, photo_path, embedding_path, registered)
VALUES
('TENANT001', '22CSE001', 'Anant Kumar',    1, 'data/student_photos/TENANT001/22CSE001_Anant.jpg',  'data/embeddings/TENANT001/22CSE001.pkl', FALSE),
('TENANT001', '22CSE002', 'Rohan Vashisht', 1, 'data/student_photos/TENANT001/22CSE002_Rohan.jpg',  'data/embeddings/TENANT001/22CSE002.pkl', FALSE),
('TENANT001', '22CSE003', 'Yug Verma',      1, 'data/student_photos/TENANT001/22CSE003_Yug.jpg',    'data/embeddings/TENANT001/22CSE003.pkl', TRUE),
('TENANT001', '22CSE004', 'Vasu Aggarwal',  1, 'data/student_photos/TENANT001/22CSE004_Vasu.jpg',   'data/embeddings/TENANT001/22CSE004.pkl', FALSE),
('TENANT001', '22CSE005', 'Test Student 1', 1, 'data/student_photos/TENANT001/22CSE005_Test1.jpg',  'data/embeddings/TENANT001/22CSE005.pkl', FALSE),
('TENANT001', '22CSE006', 'Test Student 2', 1, 'data/student_photos/TENANT001/22CSE006_Test2.jpg',  'data/embeddings/TENANT001/22CSE006.pkl', FALSE);

-- Room + DroidCam (replace IP with your actual DroidCam IP)
INSERT INTO room_cameras (tenant_id, room_no, rtsp_url, label)
VALUES ('TENANT001', 'A201', 'rtsp://192.168.1.100:4747/video', 'DroidCam A201');

-- Timetable (adjust times to whatever you want to test with)
INSERT INTO timetable (tenant_id, room_no, section_id, subject, faculty, day_of_week, start_time, end_time)
VALUES
('TENANT001', 'A201', 1, 'Data Structures',        'Dr. Sharma',  'MON', '10:00', '11:00'),
('TENANT001', 'A201', 1, 'Database Management',    'Dr. Gupta',   'MON', '11:00', '12:00'),
('TENANT001', 'A201', 1, 'Machine Learning',        'Dr. Verma',   'TUE', '10:00', '11:00'),
('TENANT001', 'A201', 1, 'Computer Networks',       'Dr. Singh',   'WED', '09:00', '10:00'),
('TENANT001', 'A201', 1, 'Software Engineering',    'Dr. Sharma',  'THU', '11:00', '12:00');
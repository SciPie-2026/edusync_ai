from app.db.connection import get_connection, get_cursor


def get_session_for_room(tenant_id, room_no, day, time):
    """
    Given room + current day + time, find what class is running.
    """
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("""
        SELECT t.id, t.subject, t.faculty, t.start_time, t.end_time,
               s.id as section_id, s.name as section_name
        FROM timetable t
        JOIN sections s ON s.id = t.section_id
        WHERE t.tenant_id = %s
        AND t.room_no = %s
        AND t.day_of_week = %s
        AND t.start_time <= %s
        AND t.end_time > %s
    """, (tenant_id, room_no, day, time, time))
    result = cur.fetchone()
    conn.close()
    return result


def get_students_for_section(tenant_id, section_id):
    """
    Load all registered students for a section.
    """
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("""
        SELECT id, roll_no, name, embedding_path
        FROM students
        WHERE tenant_id = %s
        AND section_id = %s
        AND registered = TRUE
    """, (tenant_id, section_id))
    result = cur.fetchall()
    conn.close()
    return result


def get_camera_for_room(tenant_id, room_no):
    """
    Get RTSP link for a room.
    """
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("""
        SELECT rtsp_url FROM room_cameras
        WHERE tenant_id = %s AND room_no = %s AND active = TRUE
    """, (tenant_id, room_no))
    result = cur.fetchone()
    conn.close()
    return result


def create_session(tenant_id, timetable_id, room_no, section_id, subject, date, start_time, end_time):
    conn = get_connection()
    cur = get_cursor(conn)
    cur.execute("""
        INSERT INTO sessions
        (tenant_id, timetable_id, room_no, section_id, subject, date, start_time, end_time, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'scheduled')
        RETURNING id
    """, (tenant_id, timetable_id, room_no, section_id, subject, date, start_time, end_time))
    session_id = cur.fetchone()["id"]
    conn.commit()
    conn.close()
    return session_id


def log_attendance(tenant_id, session_id, student_id, scan_number):
    """
    Mark a student present for a specific scan.
    Creates attendance row if not exists, updates scan column.
    """
    conn = get_connection()
    cur = get_cursor(conn)

    scan_col = f"scan_{scan_number}"

    # upsert attendance row
    cur.execute("""
        INSERT INTO attendance (tenant_id, session_id, student_id)
        VALUES (%s, %s, %s)
        ON CONFLICT (session_id, student_id) DO NOTHING
    """, (tenant_id, session_id, student_id))

    cur.execute(f"""
        UPDATE attendance
        SET {scan_col} = TRUE,
            final_status = 'present'
        WHERE session_id = %s AND student_id = %s
    """, (session_id, student_id))

    conn.commit()
    conn.close()


def get_rtsp_for_room(tenant_id, room_no):
    return get_camera_for_room(tenant_id, room_no)
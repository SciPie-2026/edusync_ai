import time
import pickle
import numpy as np
import cv2
from datetime import datetime, timedelta
from app.db.queries import (
    get_session_for_room,
    get_students_for_section,
    get_camera_for_room,
    create_session,
    log_attendance
)
from app.core.detector import run_scan

TENANT_ID = "TENANT001"
ROOM_NO   = "A201"
NUM_SCANS = 3


def load_embeddings_for_section(students):
    known_embeddings = {}
    for student in students:
        path = student["embedding_path"]
        if not path:
            continue
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            known_embeddings[student["roll_no"]] = data["embedding"]
        except FileNotFoundError:
            print(f"[WARN] Embedding not found for {student['roll_no']}")
    return known_embeddings


def grab_frame_from_source(source):
    cap = cv2.VideoCapture(source)
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print(f"[ERROR] Could not grab frame from {source}")
        return None
    return frame


def calculate_scan_times(start_time, end_time, num_scans=3):
    buffer   = timedelta(minutes=5)
    start    = start_time + buffer
    end      = end_time - buffer
    duration = (end - start).total_seconds()
    interval = duration / (num_scans - 1) if num_scans > 1 else duration

    scan_times = []
    for i in range(num_scans):
        scan_times.append(start + timedelta(seconds=interval * i))
    return scan_times


def run_session(timetable_row, session_id, known_embeddings, rtsp_url=0):
    now      = datetime.now()
    date     = now.date()
    start_dt = datetime.combine(date, timetable_row["start_time"])
    end_dt   = datetime.combine(date, timetable_row["end_time"])

    scan_times = calculate_scan_times(start_dt, end_dt, NUM_SCANS)

    print(f"\n[SESSION] {timetable_row['subject']} — {timetable_row['section_name']}")
    print(f"[SESSION] Room: {ROOM_NO}")
    print(f"[SESSION] Scans at: {[t.strftime('%H:%M:%S') for t in scan_times]}")

    for scan_number, scan_time in enumerate(scan_times, start=1):
        wait_seconds = (scan_time - datetime.now()).total_seconds()
        if wait_seconds > 0:
            print(f"\n[SCAN {scan_number}] Waiting {wait_seconds:.0f}s until {scan_time.strftime('%H:%M:%S')}...")
            time.sleep(wait_seconds)

        print(f"[SCAN {scan_number}] Grabbing frame from source: {rtsp_url}")
        frame = grab_frame_from_source(rtsp_url)

        if frame is None:
            print(f"[SCAN {scan_number}] Skipped — no frame.")
            continue

        cv2.imwrite("data/last_scan.jpg", frame)
        results = run_scan(frame, known_embeddings)
        print(f"[SCAN {scan_number}] Matches found: {len(results)}")

        for match in results:
            roll_no        = match["student_id"]
            student_db_id  = get_student_db_id(TENANT_ID, roll_no)
            if student_db_id:
                log_attendance(TENANT_ID, session_id, student_db_id, scan_number)
                print(f"[SCAN {scan_number}] ✓ {roll_no} marked present (similarity: {match['similarity']})")
            else:
                print(f"[SCAN {scan_number}] ✗ {roll_no} not found in DB")

    print(f"\n[SESSION] Complete — all {NUM_SCANS} scans done.")


def get_student_db_id(tenant_id, roll_no):
    from app.db.connection import get_connection, get_cursor
    conn = get_connection()
    cur  = get_cursor(conn)
    cur.execute("""
        SELECT id FROM students
        WHERE tenant_id = %s AND roll_no = %s
    """, (tenant_id, roll_no))
    row = cur.fetchone()
    conn.close()
    return row["id"] if row else None


def check_and_run():
    print(f"[SCHEDULER] Started. Watching room {ROOM_NO} for tenant {TENANT_ID}")
    print(f"[SCHEDULER] Checking timetable every 60 seconds...\n")

    while True:
        now          = datetime.now()
        day          = now.strftime("%a").upper()[:3]
        current_time = now.strftime("%H:%M")

        timetable_row = get_session_for_room(
            TENANT_ID, ROOM_NO, day, current_time
        )

        if timetable_row:
            print(f"[SCHEDULER] Class found: {timetable_row['subject']} at {current_time}")

            camera           = get_camera_for_room(TENANT_ID, ROOM_NO)
            rtsp_url         = camera["rtsp_url"] if camera else 0
            students         = get_students_for_section(TENANT_ID, timetable_row["section_id"])
            known_embeddings = load_embeddings_for_section(students)

            print(f"[SCHEDULER] Loaded {len(known_embeddings)} embeddings")

            session_id = create_session(
                TENANT_ID,
                timetable_row["id"],
                ROOM_NO,
                timetable_row["section_id"],
                timetable_row["subject"],
                now.date(),
                timetable_row["start_time"],
                timetable_row["end_time"]
            )

            run_session(timetable_row, session_id, known_embeddings, rtsp_url)

            end_dt      = datetime.combine(now.date(), timetable_row["end_time"])
            sleep_secs  = (end_dt - datetime.now()).total_seconds()
            if sleep_secs > 0:
                print(f"[SCHEDULER] Sleeping until class ends ({sleep_secs:.0f}s)...")
                time.sleep(sleep_secs)
        else:
            print(f"[SCHEDULER] No class at {current_time} on {day}. Checking again in 60s...")
            time.sleep(60)


if __name__ == "__main__":
    check_and_run()
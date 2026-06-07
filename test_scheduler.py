from datetime import datetime, timedelta
from app.core.scheduler import (
    load_embeddings_for_section,
    run_session
)
from app.db.queries import get_students_for_section, create_session

TENANT_ID  = "TENANT001"
ROOM_NO    = "A201"
SECTION_ID = 1

# load students + embeddings
students = get_students_for_section(TENANT_ID, SECTION_ID)
known_embeddings = load_embeddings_for_section(students)
print(f"Loaded {len(known_embeddings)} embeddings: {list(known_embeddings.keys())}")

# create a test session starting now, ending in 3 minutes
now      = datetime.now()
end_time = now + timedelta(minutes=3)

session_id = create_session(
    TENANT_ID, 1, ROOM_NO, SECTION_ID,
    "Test Subject",
    now.date(),
    now.time(),
    end_time.time()
)
print(f"Test session created: ID {session_id}")

# fake timetable row
timetable_row = {
    "id": 1,
    "subject": "Test Subject",
    "section_name": "BT-FSD-A",
    "start_time": now.time(),
    "end_time": end_time.time()
}

# 0 = webcam, replace with rtsp_url string for real camera
run_session(timetable_row, session_id, known_embeddings, rtsp_url=0)
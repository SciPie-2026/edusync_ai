import cv2
import time
from app.core.detector import (
    stage1_detect_heads,
    stage2_recognize_faces,
    draw_results
)

known_embeddings = {}

cap = cv2.VideoCapture(0)
print("Two-stage detection running. Press 'q' to quit.")

prev_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    head_boxes = stage1_detect_heads(frame)

    matches = []
    if head_boxes:
        matches = stage2_recognize_faces(frame, head_boxes, known_embeddings)

    frame = draw_results(frame, head_boxes, matches)

    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 200, 0), 2)
    cv2.putText(frame, f"Heads: {len(head_boxes)}  Matched: {len(matches)}",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 255), 2)

    cv2.imshow("EduSync AI - Two Stage Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
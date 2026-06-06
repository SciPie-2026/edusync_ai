import cv2
import pickle
import numpy as np
import time
from app.core.detector import run_scan

# Load your embedding
with open("data/embeddings/YUG.pkl", "rb") as f:
    data = pickle.load(f)

known_embeddings = {
    data["student_id"]: data["embedding"]
}

print(f"Loaded embeddings for: {list(known_embeddings.keys())}")
print("Taking snapshot in 3 seconds... look at the camera.")
time.sleep(3)

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if not ret:
    print("ERROR: Could not grab frame.")
    exit()

cv2.imwrite("data/last_scan.jpg", frame)
print("Snapshot saved.")

results = run_scan(frame, known_embeddings)

print(f"\n── Scan Results ──────────────────────")
print(f"Matches found: {len(results)}")
for r in results:
    print(f"  → {r['student_id']} | similarity: {r['similarity']}")
print(f"──────────────────────────────────────")
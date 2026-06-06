import cv2
import numpy as np
import os
import uuid
import time
from ultralytics import YOLO
from insightface.app import FaceAnalysis

# ── Models ─────────────────────────────────────────────────────────────────────
yolo_model = YOLO("yolov8n-pose.pt")

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
)
face_app.prepare(ctx_id=0, det_size=(320, 320))

TEMP_DIR = "data/temp_crops"
os.makedirs(TEMP_DIR, exist_ok=True)


# ── Core scan function ─────────────────────────────────────────────────────────
def run_scan(frame, known_embeddings):
    """
    Full pipeline:
    1. YOLO detects heads in frame
    2. Crop each head region
    3. InsightFace generates embedding from crop
    4. Match against known_embeddings
    5. Delete temp crops
    6. Return matched student IDs
    """
    results = []

    # Stage 1 — YOLO head detection
    head_crops = extract_head_crops(frame)

    if not head_crops:
        print("[SCAN] No heads detected in frame.")
        return results

    print(f"[SCAN] {len(head_crops)} head(s) detected. Running InsightFace...")

    # Stage 2 — InsightFace on each crop
    for crop, temp_path in head_crops:
        try:
            faces = face_app.get(crop)
            for face in faces:
                if face.embedding is None:
                    continue
                student_id, score = match_embedding(
                    face.embedding, known_embeddings
                )
                if student_id:
                    print(f"[SCAN] Matched: {student_id} ({score:.2f})")
                    results.append({
                        "student_id": student_id,
                        "similarity": round(score, 3),
                        "timestamp": time.time()
                    })
        finally:
            # Always delete temp crop
            if os.path.exists(temp_path):
                os.remove(temp_path)

    return results


# ── Head extraction ────────────────────────────────────────────────────────────
def extract_head_crops(frame, conf_thresh=0.6):
    """
    Run YOLO on frame.
    For each detected person, crop the head region (top 35% of body box).
    Save as temp file, return list of (crop_array, temp_path).
    """
    yolo_results = yolo_model(frame, verbose=False, conf=conf_thresh, device="cuda")[0]
    crops = []

    if yolo_results.boxes is None:
        return crops

    h, w = frame.shape[:2]

    for box in yolo_results.boxes:
        conf = float(box.conf[0])
        if conf < conf_thresh:
            continue

        x1, y1, x2, y2 = map(int, box.xyxy[0])

        # head = top 35% of person bounding box + padding
        head_y2 = y1 + int((y2 - y1) * 0.35)
        pad = 20
        cx1 = max(0, x1 - pad)
        cy1 = max(0, y1 - pad)
        cx2 = min(w, x2 + pad)
        cy2 = min(h, head_y2 + pad)

        crop = frame[cy1:cy2, cx1:cx2]
        if crop.size == 0:
            continue

        # save temp
        temp_path = os.path.join(TEMP_DIR, f"{uuid.uuid4().hex}.jpg")
        cv2.imwrite(temp_path, crop)
        crops.append((crop, temp_path))

    return crops


# ── Embedding match ────────────────────────────────────────────────────────────
def match_embedding(embedding, known_embeddings, threshold=0.5):
    """
    Cosine similarity match.
    known_embeddings: { student_id: np.array }
    Returns (student_id, score) or (None, 0)
    """
    best_id = None
    best_score = 0.0

    for student_id, known_emb in known_embeddings.items():
        score = cosine_similarity(embedding, known_emb)
        if score > best_score:
            best_score = score
            best_id = student_id

    if best_score >= threshold:
        return best_id, best_score
    return None, 0.0


def cosine_similarity(a, b):
    a, b = np.array(a), np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-6))
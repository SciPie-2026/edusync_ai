import cv2
import time
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n-pose.pt")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# ── Cyberpunk colors (BGR) ─────────────────────────────────────────────────────
NEON_CYAN    = (255, 255, 0)
NEON_PINK    = (180, 0, 255)
NEON_YELLOW  = (0, 255, 255)
NEON_ORANGE  = (0, 165, 255)
NEON_GREEN   = (0, 255, 128)
BOX_COLOR    = (255, 0, 200)
OVERLAY_COLOR= (20, 0, 40)

# ── Keypoint names ─────────────────────────────────────────────────────────────
KP_NAMES = [
    "nose", "l_eye", "r_eye", "l_ear", "r_ear",
    "l_shldr", "r_shldr", "l_elbow", "r_elbow",
    "l_wrist", "r_wrist", "l_hip", "r_hip",
    "l_knee", "r_knee", "l_ankle", "r_ankle"
]

# ── Which keypoints get a highlight box ───────────────────────────────────────
BOXED_PARTS = {
    0:  ("HEAD",    NEON_CYAN,   18),
    9:  ("L.HAND",  NEON_PINK,   14),
    10: ("R.HAND",  NEON_PINK,   14),
    15: ("L.FOOT",  NEON_ORANGE, 14),
    16: ("R.FOOT",  NEON_ORANGE, 14),
}

# ── Skeleton connections with per-segment color ────────────────────────────────
SKELETON = [
    (0, 1,  NEON_CYAN),   (0, 2,  NEON_CYAN),
    (1, 3,  NEON_CYAN),   (2, 4,  NEON_CYAN),
    (5, 6,  NEON_GREEN),
    (5, 7,  NEON_GREEN),  (7, 9,  NEON_PINK),
    (6, 8,  NEON_GREEN),  (8, 10, NEON_PINK),
    (5, 11, NEON_YELLOW), (6, 12, NEON_YELLOW),
    (11, 12, NEON_YELLOW),
    (11, 13, NEON_ORANGE),(13, 15, NEON_ORANGE),
    (12, 14, NEON_ORANGE),(14, 16, NEON_ORANGE),
]

prev_time = time.time()
frame_count = 0

def draw_cyberpunk_box(frame, cx, cy, label, color, size=18):
    """Draw a corner-bracket box around a keypoint with a label."""
    x1, y1 = cx - size, cy - size
    x2, y2 = cx + size, cy + size
    t = 6  # bracket length

    # corner brackets
    pts = [
        ((x1, y1), (x1+t, y1), (x1, y1+t)),
        ((x2, y1), (x2-t, y1), (x2, y1+t)),
        ((x1, y2), (x1+t, y2), (x1, y2-t)),
        ((x2, y2), (x2-t, y2), (x2, y2-t)),
    ]
    for corner in pts:
        cv2.line(frame, corner[0], corner[1], color, 2)
        cv2.line(frame, corner[0], corner[2], color, 2)

    # label background
    (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
    cv2.rectangle(frame, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
    cv2.putText(frame, label, (x1 + 2, y1 - 3),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)

def draw_glowing_line(frame, p1, p2, color, thickness=2):
    """Simulate glow by drawing thick dim line under bright line."""
    dim = tuple(max(0, int(c * 0.3)) for c in color)
    cv2.line(frame, p1, p2, dim, thickness + 4)
    cv2.line(frame, p1, p2, color, thickness)

print("EduSync Cyberpunk Pose — Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # dark overlay for cyberpunk feel
    overlay = np.full(frame.shape, OVERLAY_COLOR, dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.85, overlay, 0.15, 0)

    results = model(frame, verbose=False, conf=0.6, device="cuda")[0]

    person_count = 0

    if results.keypoints is not None:
        kps_conf_all = results.keypoints.conf
        for idx, person_kps in enumerate(results.keypoints.xy):
            kps = person_kps.cpu().numpy()
            confs = kps_conf_all[idx].cpu().numpy() if kps_conf_all is not None else [1.0] * len(kps)
            person_count += 1

            # draw skeleton lines
            for a, b, color in SKELETON:
                if a < len(kps) and b < len(kps):
                    x1, y1 = kps[a]
                    x2, y2 = kps[b]
                    if x1 > 0 and y1 > 0 and x2 > 0 and y2 > 0:
                        draw_glowing_line(frame, (int(x1), int(y1)),
                                          (int(x2), int(y2)), color, 2)

            # draw keypoints + labels
            for i, (x, y) in enumerate(kps):
                if x <= 0 or y <= 0:
                    continue
                cx, cy = int(x), int(y)

                if i in BOXED_PARTS:
                    label, color, size = BOXED_PARTS[i]
                    draw_cyberpunk_box(frame, cx, cy, label, color, size)
                    cv2.circle(frame, (cx, cy), 5, color, -1)
                else:
                    # small dot + tiny label for other keypoints
                    cv2.circle(frame, (cx, cy), 3, NEON_GREEN, -1)
                    name = KP_NAMES[i] if i < len(KP_NAMES) else str(i)
                    cv2.putText(frame, name, (cx + 5, cy - 5),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.32, NEON_GREEN, 1)

    # person bounding boxes
    if results.boxes is not None:
        for box in results.boxes:
            if float(box.conf[0]) >= 0.6:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = float(box.conf[0])
                # corner bracket style box
                t = 16
                for (px, py), (dx, dy) in [
                    ((x1,y1),(t,0)), ((x1,y1),(0,t)),
                    ((x2,y1),(-t,0)),((x2,y1),(0,t)),
                    ((x1,y2),(t,0)), ((x1,y2),(0,-t)),
                    ((x2,y2),(-t,0)),((x2,y2),(0,-t)),
                ]:
                    cv2.line(frame,(px,py),(px+dx,py+dy),BOX_COLOR,2)
                cv2.putText(frame, f"PERSON {conf:.0%}",
                            (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, BOX_COLOR, 1)

    # ── HUD ───────────────────────────────────────────────────────────────────
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    frame_count += 1

    cv2.putText(frame, f"EDUSYNC AI", (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEON_CYAN, 2)
    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEON_YELLOW, 1)
    cv2.putText(frame, f"DETECTED: {person_count}", (10, 72),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEON_PINK, 1)
    cv2.putText(frame, f"CONF: 60%+", (10, 94),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEON_GREEN, 1)

    cv2.imshow("EDUSYNC // CYBERPUNK POSE", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
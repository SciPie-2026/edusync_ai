import cv2
import time
import math
import random
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n-pose.pt")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_FPS, 60)

KP_CONF = 0.40

# ── Palette (BGR) — Terminator Red + Endoskeleton Dark ────────────────────────
T_RED         = (0,   0,   220)   # core threat red
T_RED_DIM     = (0,   0,    80)   # dim red
T_RED_GLOW    = (20,  20,  255)   # bright red glow
T_ORANGE      = (0,   80,  230)   # HK targeting amber
T_ORANGE_DIM  = (0,   30,   90)
T_GREY        = (90,  90,   90)   # endoskeleton steel
T_GREY_DIM    = (40,  40,   40)
T_WHITE       = (200, 210, 220)   # HUD readout
T_PLASMA_A    = (30,  30,  255)   # plasma arc red
T_PLASMA_B    = (0,   60,  180)   # plasma arc orange
OVERLAY_DARK  = (4,   4,    10)   # near-black overlay

KP_NAMES = [
    "nose","l_eye","r_eye","l_ear","r_ear",
    "l_shldr","r_shldr","l_elbow","r_elbow",
    "l_wrist","r_wrist","l_hip","r_hip",
    "l_knee","r_knee","l_ankle","r_ankle"
]

BOXED_PARTS = {
    0:  ("CPU-CORE",    T_RED,     22),
    5:  ("L-SERVO",     T_ORANGE,  14),
    6:  ("R-SERVO",     T_ORANGE,  14),
    9:  ("L-ARM",       T_RED_GLOW,16),
    10: ("R-ARM",       T_RED_GLOW,16),
    11: ("L-CHASSIS",   T_GREY,    14),
    12: ("R-CHASSIS",   T_GREY,    14),
    15: ("L-ACTUATOR",  T_ORANGE,  14),
    16: ("R-ACTUATOR",  T_ORANGE,  14),
}

SKELETON = [
    (0,  1,  T_RED_DIM), (0,  2, T_RED_DIM),
    (1,  3,  T_RED_DIM), (2,  4, T_RED_DIM),
    (5,  6,  T_RED),
    (5,  7,  T_ORANGE),  (7,  9, T_ORANGE),
    (6,  8,  T_ORANGE),  (8, 10, T_ORANGE),
    (5, 11,  T_RED),     (6, 12, T_RED),
    (11,12,  T_RED),
    (11,13,  T_ORANGE),  (13,15, T_ORANGE),
    (12,14,  T_ORANGE),  (14,16, T_ORANGE),
]

prev_time   = time.time()
start_time  = time.time()
frame_count = 0
FONT        = cv2.FONT_HERSHEY_SIMPLEX

last_hull = None   # numpy hull persistence


# ── Scan-noise generator ───────────────────────────────────────────────────────
def add_scan_noise(frame, intensity=0.04):
    """Sparse red pixel noise simulating CRT/thermal sensor artifact."""
    h, w = frame.shape[:2]
    n = int(w * h * intensity)
    xs = np.random.randint(0, w, n)
    ys = np.random.randint(0, h, n)
    vals = np.random.randint(30, 140, (n, 3), dtype=np.uint8)
    vals[:, :2] = 0   # only red channel (BGR → zero B,G)
    frame[ys, xs] = vals


# ── Helpers ────────────────────────────────────────────────────────────────────

def glow_line(frame, p1, p2, color, thick=2):
    dim = tuple(max(0, int(c * 0.18)) for c in color)
    mid = tuple(max(0, int(c * 0.45)) for c in color)
    cv2.line(frame, p1, p2, dim,   thick + 8)
    cv2.line(frame, p1, p2, mid,   thick + 3)
    cv2.line(frame, p1, p2, color, thick)


def glow_circle(frame, center, radius, color, thick=1):
    dim = tuple(max(0, int(c * 0.25)) for c in color)
    cv2.circle(frame, center, radius + 4, dim,   thick + 2)
    cv2.circle(frame, center, radius,     color, thick)


def bracket_box(frame, cx, cy, label, color, size=18):
    x1, y1 = cx - size, cy - size
    x2, y2 = cx + size, cy + size
    arm = max(8, size // 2)
    for c in [
        ((x1,y1),(x1+arm,y1),(x1,y1+arm)),
        ((x2,y1),(x2-arm,y1),(x2,y1+arm)),
        ((x1,y2),(x1+arm,y2),(x1,y2-arm)),
        ((x2,y2),(x2-arm,y2),(x2,y2-arm)),
    ]:
        cv2.line(frame, c[0], c[1], color, 2)
        cv2.line(frame, c[0], c[2], color, 2)
    (tw, th), _ = cv2.getTextSize(label, FONT, 0.36, 1)
    cv2.rectangle(frame, (x1, y1-th-6), (x1+tw+6, y1), color, -1)
    cv2.putText(frame, label, (x1+3, y1-3), FONT, 0.36, (0, 0, 0), 1)
    for px, py in [(x1,y1),(x2,y1),(x1,y2),(x2,y2)]:
        cv2.circle(frame, (px,py), 2, color, -1)


def draw_threat_reticle(frame, cx, cy, radius, color, t, idx=0):
    """Rotating segmented targeting ring — Terminator HK style."""
    segs = 8
    gap_frac = 0.25
    rot = t * 1.8 * (1 if idx % 2 == 0 else -1)
    for i in range(segs):
        a_start = rot + i * (2 * math.pi / segs)
        a_end   = a_start + (2 * math.pi / segs) * (1 - gap_frac)
        pts_arc = []
        steps = 8
        for s in range(steps + 1):
            a = a_start + (a_end - a_start) * s / steps
            pts_arc.append((int(cx + radius * math.cos(a)),
                            int(cy + radius * math.sin(a))))
        for j in range(len(pts_arc) - 1):
            cv2.line(frame, pts_arc[j], pts_arc[j+1], color, 2)
    # inner crosshair ticks
    for angle in [0, math.pi/2, math.pi, 3*math.pi/2]:
        a = angle + rot * 0.5
        ix = int(cx + (radius - 8) * math.cos(a))
        iy = int(cy + (radius - 8) * math.sin(a))
        ox = int(cx + (radius + 8) * math.cos(a))
        oy = int(cy + (radius + 8) * math.sin(a))
        cv2.line(frame, (ix, iy), (ox, oy), color, 1)


def draw_person_box(frame, x1, y1, x2, y2, conf, pid):
    arm = 20
    for (px,py),(dx,dy) in [
        ((x1,y1),(arm,0)),((x1,y1),(0,arm)),
        ((x2,y1),(-arm,0)),((x2,y1),(0,arm)),
        ((x1,y2),(arm,0)),((x1,y2),(0,-arm)),
        ((x2,y2),(-arm,0)),((x2,y2),(0,-arm)),
    ]:
        cv2.line(frame,(px,py),(px+dx,py+dy),T_RED,2)
    mid_y = (y1+y2)//2
    for ex in [x1,x2]:
        cv2.line(frame,(ex,mid_y-20),(ex,mid_y+20),T_RED_DIM,1)
    header = f"TARGET {pid+1:02d}  |  THREAT {conf:.0%}"
    (tw,_),_ = cv2.getTextSize(header,FONT,0.42,1)
    cv2.rectangle(frame,(x1,y1-18),(x1+tw+10,y1),T_RED,-1)
    cv2.putText(frame,header,(x1+5,y1-4),FONT,0.42,(0,0,0),1)
    cv2.putText(frame,f"H:{y2-y1}px",(x1+4,y2+14),FONT,0.38,T_RED_DIM,1)


# ── Terminator endoskeleton joint pulse ────────────────────────────────────────

def draw_joint_pulse(frame, cx, cy, t, idx=0):
    """Concentric shrinking red rings — like a CPU heat-sink pulse."""
    phase = (t * 4 + idx * 1.3) % (2 * math.pi)
    for ring in range(3):
        offset = ring * (2 * math.pi / 3)
        r_frac = (math.sin(phase + offset) + 1) / 2   # 0..1
        radius = int(6 + r_frac * 14)
        alpha  = 0.3 + 0.5 * r_frac
        col    = T_RED if ring == 0 else T_RED_DIM
        ov = frame.copy()
        cv2.circle(ov, (cx, cy), radius, col, 1)
        cv2.addWeighted(ov, alpha, frame, 1 - alpha, 0, frame)
    cv2.circle(frame, (cx, cy), 3, T_RED_GLOW, -1)


# ── HK scanner box (replaces fireball at wrists) ──────────────────────────────

def draw_hk_lock(frame, cx, cy, t, idx=0):
    """
    Multi-ring threat-lock reticle at hand position.
    Simulates a Terminator HK targeting system locking on.
    """
    flicker = random.random() > 0.06   # occasional digital flicker off

    if not flicker:
        return

    # outer slow ring
    draw_threat_reticle(frame, cx, cy, 38, T_ORANGE, t, idx)
    # inner fast ring
    draw_threat_reticle(frame, cx, cy, 22, T_RED_GLOW, t * 2.2, idx + 1)

    # crosshair lines
    for angle, length in [(0, 18), (math.pi/2, 18)]:
        a1 = (int(cx + math.cos(angle) * (6)),
              int(cy + math.sin(angle) * (6)))
        a2 = (int(cx + math.cos(angle) * length),
              int(cy + math.sin(angle) * length))
        a3 = (int(cx - math.cos(angle) * (6)),
              int(cy - math.sin(angle) * (6)))
        a4 = (int(cx - math.cos(angle) * length),
              int(cy - math.sin(angle) * length))
        cv2.line(frame, a1, a2, T_RED_GLOW, 1)
        cv2.line(frame, a3, a4, T_RED_GLOW, 1)

    # center hot dot
    cv2.circle(frame, (cx, cy), 5,  T_RED_GLOW, -1)
    cv2.circle(frame, (cx, cy), 10, T_ORANGE,   1)

    # "LOCK" readout
    lock_text = "LOCK" if int(t * 4) % 2 == 0 else "ACQ."
    cv2.putText(frame, lock_text, (cx - 14, cy + 54),
                FONT, 0.38, T_RED_GLOW, 1)


# ── Plasma arc outline (replaces lightning — deeper red/orange) ────────────────

def zigzag_between(p1, p2, amplitude=12, segments=8):
    pts = []
    x1, y1 = p1;  x2, y2 = p2
    dx = (x2-x1)/segments;  dy = (y2-y1)/segments
    length = max(math.hypot(dx,dy), 1)
    px = -dy/length;  py = dx/length
    for i in range(segments+1):
        fx = x1 + dx*i;  fy = y1 + dy*i
        if 0 < i < segments:
            j = random.uniform(-amplitude, amplitude)
            fx += px*j;  fy += py*j
        pts.append((int(fx), int(fy)))
    return pts


def draw_plasma_outline(frame, hull):
    """Red-orange plasma arcs tracing the body hull — Skynet scan effect."""
    if hull is None or len(hull) < 3:
        return
    if random.random() < 0.15:   # strobe flicker
        return

    pts = [tuple(p[0]) for p in hull]
    n   = len(pts)

    for i in range(n):
        p1 = pts[i];  p2 = pts[(i+1) % n]
        for strand in range(2):
            amp  = 12 if strand == 0 else 5
            segs = random.randint(5, 9)
            path = zigzag_between(p1, p2, amplitude=amp, segments=segs)
            col  = T_PLASMA_A if strand == 0 else T_PLASMA_B
            width = 3 if strand == 0 else 1
            for j in range(len(path)-1):
                a, b = path[j], path[j+1]
                cv2.line(frame, a, b, col, width)
            # thin bright core line
            for j in range(len(path)-1):
                cv2.line(frame, path[j], path[j+1], (40, 40, 255), 1)

    # random arc sparks along hull
    for _ in range(random.randint(1, 4)):
        bx, by = random.choice(pts)
        angle  = random.uniform(0, 2*math.pi)
        length = random.uniform(8, 28)
        ex = int(bx + math.cos(angle)*length)
        ey = int(by + math.sin(angle)*length)
        path = zigzag_between((bx,by),(ex,ey), amplitude=5, segments=4)
        for j in range(len(path)-1):
            cv2.line(frame, path[j], path[j+1], T_PLASMA_A, 1)


# ── Body silhouette ────────────────────────────────────────────────────────────

def draw_body_outline(frame, kps, confs):
    visible = [
        (int(x), int(y))
        for i,(x,y) in enumerate(kps)
        if confs[i] >= KP_CONF and x > 0 and y > 0
    ]
    if len(visible) < 4:
        return None
    pts  = np.array(visible, np.int32).reshape((-1,1,2))
    hull = cv2.convexHull(pts)
    ov   = frame.copy()
    cv2.fillConvexPoly(ov, hull, (8, 0, 22))    # dark crimson fill
    cv2.addWeighted(ov, 0.28, frame, 0.72, 0, frame)
    return hull


# ── Scan line ─────────────────────────────────────────────────────────────────

def draw_scan_line(frame, scan_y):
    w = frame.shape[1]
    cv2.line(frame,(0,scan_y),(w,scan_y),(0,0,160),1)
    for offset,alpha in [(1,0.35),(3,0.12),(6,0.05)]:
        if scan_y-offset >= 0:
            ov = frame.copy()
            cv2.line(ov,(0,scan_y-offset),(w,scan_y-offset),(0,0,160),1)
            cv2.addWeighted(ov,alpha,frame,1-alpha,0,frame)


# ── HUD ───────────────────────────────────────────────────────────────────────

def draw_hud_frame(frame, fps, person_count, t):
    h, w = frame.shape[:2]
    elapsed = time.time() - start_time

    # corner brackets
    for (ox,oy,sx,sy) in [(0,0,1,1),(w,0,-1,1),(0,h,1,-1),(w,h,-1,-1)]:
        cv2.line(frame,(ox,oy),(ox+sx*80,oy),T_RED,1)
        cv2.line(frame,(ox,oy),(ox,oy+sy*80),T_RED,1)
        cv2.line(frame,(ox+sx*8,oy+sy*8),(ox+sx*50,oy+sy*8),T_ORANGE,2)
        cv2.line(frame,(ox+sx*8,oy+sy*8),(ox+sx*8,oy+sy*50),T_ORANGE,2)

    # title bar
    title = "CYBERDYNE SYSTEMS // T-800 VISION OS v2.29.4"
    (tw,_),_ = cv2.getTextSize(title,FONT,0.62,1)
    tx = (w-tw)//2
    cv2.rectangle(frame,(tx-8,6),(tx+tw+8,34),(0,0,0),-1)
    cv2.putText(frame,title,(tx,28),FONT,0.62,T_RED,1)
    cv2.line(frame,(w//2-400,38),(w//2+400,38),T_RED_DIM,1)

    # left telemetry
    threat_str = "TERMINATED" if person_count == 0 else f"TRACKING:{person_count:02d}"
    left_data = [
        ("SYS.CLOCK",   f"{elapsed:07.2f}s"),
        ("FRAME.RATE",  f"{fps:05.1f}"),
        ("CONTACTS",    f"{person_count:02d}"),
        ("KP.THRESH",   f"{KP_CONF:.0%}"),
        ("RESOLUTION",  "1280x720"),
        ("CLASSIFIER",  "YOLOv8n-POSE"),
        ("MISSION",     threat_str),
        ("POWER.CORE",  "NUCLEAR CELL"),
    ]
    for i,(key,val) in enumerate(left_data):
        y = 70 + i*26
        cv2.putText(frame,key,(14,y),FONT,0.44,T_ORANGE,1)
        cv2.putText(frame,f": {val}",(148,y),FONT,0.44,T_WHITE,1)

    # right telemetry
    right_data = [
        ("ENDOSKELETON","INTACT"),
        ("HYDRAULICS",  "NOMINAL"),
        ("THREAT.LVL",  "EXTREME"),
        ("WEAPONS.SYS", "ARM"),
        ("PLASMA.ARC",  "ACTIVE"),
        ("TARGETING",   "LOCKED"),
        ("MISSION.OBJ", "TERMINATE"),
    ]
    for i,(key,val) in enumerate(right_data):
        y = 70 + i*26
        cv2.putText(frame,key,(w-270,y),FONT,0.44,T_ORANGE,1)
        cv2.putText(frame,f": {val}",(w-270+136,y),FONT,0.44,T_WHITE,1)

    # bottom bar
    cv2.rectangle(frame,(0,h-34),(w,h),(0,0,0),-1)
    pulse_char = "█" if int(t*6) % 2 == 0 else "▌"
    btxt = (f"  [SKYNET-NET v4.0]   FRAME:{frame_count:06d}   "
            f"UPTIME:{elapsed:06.1f}s   VISION: ONLINE   "
            f"PLASMA: ARMED   MISSION: I'LL BE BACK  {pulse_char}")
    cv2.putText(frame,btxt,(10,h-10),FONT,0.44,T_RED_DIM,1)

    # corner arc reticles
    for cx2,cy2 in [(70,h-70),(w-70,h-70)]:
        draw_threat_reticle(frame, cx2, cy2, 28, T_RED, t, 0)
        glow_circle(frame,(cx2,cy2),4,T_RED_GLOW,1)
        cv2.circle(frame,(cx2,cy2),2,T_WHITE,-1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cv2.namedWindow("CYBERDYNE // T-800 VISION OS", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("CYBERDYNE // T-800 VISION OS",
                      cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print("T-800 VISION — Press 'q' to terminate.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    t = time.time() - start_time

    # dark overlay tint
    ov = np.full(frame.shape, OVERLAY_DARK, dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.75, ov, 0.25, 0)

    # sparse CRT scan noise
    add_scan_noise(frame, intensity=0.012)

    results = model(frame, verbose=False, conf=0.45, device="cuda")[0]

    person_count = 0
    frame_hull   = None

    if results.keypoints is not None:
        kps_conf_all = results.keypoints.conf

        for idx, person_kps in enumerate(results.keypoints.xy):
            kps   = person_kps.cpu().numpy()
            confs = (kps_conf_all[idx].cpu().numpy()
                     if kps_conf_all is not None else np.ones(len(kps)))
            person_count += 1

            # body silhouette
            hull = draw_body_outline(frame, kps, confs)

            if hull is not None:
                frame_hull = hull
                last_hull  = hull
            active_hull = frame_hull if frame_hull is not None else last_hull

            draw_plasma_outline(frame, active_hull)

            # skeleton
            for a, b, color in SKELETON:
                if a >= len(kps) or b >= len(kps): continue
                if confs[a] < KP_CONF or confs[b] < KP_CONF: continue
                x1,y1 = kps[a]; x2,y2 = kps[b]
                if x1>0 and y1>0 and x2>0 and y2>0:
                    glow_line(frame,(int(x1),int(y1)),(int(x2),int(y2)),color,2)

            # keypoints
            for i,(x,y) in enumerate(kps):
                if confs[i] < KP_CONF or x<=0 or y<=0: continue
                cx_,cy_ = int(x), int(y)

                if i in (9, 10):   # wrists → HK targeting lock
                    draw_hk_lock(frame, cx_, cy_, t, idx=i)
                    bracket_box(frame, cx_, cy_, "ARM.WEAPON", T_RED_GLOW, 16)

                elif i in BOXED_PARTS:
                    label, color, size = BOXED_PARTS[i]
                    bracket_box(frame, cx_, cy_, label, color, size)
                    draw_joint_pulse(frame, cx_, cy_, t, idx=i)
                    if i == 0:   # head — extra targeting ring
                        draw_threat_reticle(frame, cx_, cy_, size+14, T_RED, t, i)

                else:
                    glow_circle(frame, (cx_,cy_), 3, T_RED_DIM, 1)
                    cv2.circle(frame, (cx_,cy_), 2, T_ORANGE, -1)

    # person bounding boxes
    if results.boxes is not None:
        for pid,box in enumerate(results.boxes):
            conf = float(box.conf[0])
            if conf >= 0.45:
                x1,y1,x2,y2 = map(int,box.xyxy[0])
                draw_person_box(frame,x1,y1,x2,y2,conf,pid)

    # scan sweep
    h_,w_ = frame.shape[:2]
    scan_y = int((t*90) % h_)
    draw_scan_line(frame, scan_y)

    # FPS + HUD
    curr_time = time.time()
    fps = 1/max(curr_time-prev_time, 1e-6)
    prev_time = curr_time

    draw_hud_frame(frame, fps, person_count, t)

    cv2.imshow("CYBERDYNE // T-800 VISION OS", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
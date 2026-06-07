import cv2
import time
import math
import random
import numpy as np
from ultralytics import YOLO

model = YOLO("yolov8n-pose.pt")

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH,  1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
cap.set(cv2.CAP_PROP_FPS, 30)

KP_CONF = 0.40

# ── Palette (BGR) ──────────────────────────────────────────────────────────────
GOLD         = (0,  200, 255)
GOLD_DIM     = (0,   80, 120)
BLUE_CORE    = (255, 200,  50)
BLUE_DIM     = (100,  60,  10)
TEAL         = (200, 220,  80)
WHITE_HUD    = (220, 230, 240)
SCAN_COLOR   = (200, 230, 255)
OVERLAY_DARK = (  5,   8,  15)
ELEC_WHITE   = (255, 255, 255)
ELEC_BLUE    = (255, 180,  60)
ELEC_PURPLE  = (220,  80, 180)
FIRE_WHITE   = (200, 230, 255)
FIRE_YELLOW  = (  0, 220, 255)
FIRE_ORANGE  = (  0, 140, 255)
FIRE_RED     = (  0,  40, 220)
FIRE_DARK    = (  0,  10,  80)

KP_NAMES = [
    "nose","l_eye","r_eye","l_ear","r_ear",
    "l_shldr","r_shldr","l_elbow","r_elbow",
    "l_wrist","r_wrist","l_hip","r_hip",
    "l_knee","r_knee","l_ankle","r_ankle"
]

BOXED_PARTS = {
    0:  ("CRANIUM",    GOLD,        20),
    5:  ("L.SHOULDER", TEAL,        14),
    6:  ("R.SHOULDER", TEAL,        14),
    9:  ("L.HAND",     FIRE_ORANGE, 16),
    10: ("R.HAND",     FIRE_ORANGE, 16),
    11: ("L.HIP",      BLUE_CORE,   14),
    12: ("R.HIP",      BLUE_CORE,   14),
    15: ("L.FOOT",     TEAL,        14),
    16: ("R.FOOT",     TEAL,        14),
}

SKELETON = [
    (0,  1,  BLUE_CORE), (0,  2, BLUE_CORE),
    (1,  3,  BLUE_CORE), (2,  4, BLUE_CORE),
    (5,  6,  GOLD),
    (5,  7,  TEAL),      (7,  9, TEAL),
    (6,  8,  TEAL),      (8, 10, TEAL),
    (5, 11,  GOLD),      (6, 12, GOLD),
    (11,12,  GOLD),
    (11,13,  TEAL),      (13,15, TEAL),
    (12,14,  TEAL),      (14,16, TEAL),
]

prev_time   = time.time()
start_time  = time.time()
frame_count = 0
FONT        = cv2.FONT_HERSHEY_SIMPLEX

# ── hull persistence (fix: never use `or` on numpy arrays) ────────────────────
last_hull = None   # stores last valid numpy hull array


# ── Particle system ────────────────────────────────────────────────────────────
class Particle:
    __slots__ = ['x','y','vx','vy','life','max_life','size']
    def __init__(self, x, y):
        angle        = random.uniform(-math.pi, 0)
        speed        = random.uniform(1.5, 5.0)
        self.x       = x + random.uniform(-6, 6)
        self.y       = y + random.uniform(-4, 4)
        self.vx      = math.cos(angle) * speed * 0.5
        self.vy      = math.sin(angle) * speed
        self.life     = 0
        self.max_life = random.randint(12, 28)
        self.size     = random.randint(3, 11)

fire_particles = {9: [], 10: []}


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
    cv2.putText(frame, label, (x1+3, y1-3), FONT, 0.36, (0,0,0), 1)
    for px, py in [(x1,y1),(x2,y1),(x1,y2),(x2,y2)]:
        cv2.circle(frame, (px,py), 2, color, -1)


def draw_arc_reticle(frame, cx, cy, radius, color, t):
    for offset in [0, math.pi, math.pi/2, 3*math.pi/2]:
        angle = t * 2.0 + offset
        ax  = int(cx + radius * math.cos(angle))
        ay  = int(cy + radius * math.sin(angle))
        ax2 = int(cx + radius * math.cos(angle + 0.6))
        ay2 = int(cy + radius * math.sin(angle + 0.6))
        cv2.line(frame, (ax,ay), (ax2,ay2), color, 2)


def draw_person_box(frame, x1, y1, x2, y2, conf, pid):
    arm = 20
    for (px,py),(dx,dy) in [
        ((x1,y1),(arm,0)),((x1,y1),(0,arm)),
        ((x2,y1),(-arm,0)),((x2,y1),(0,arm)),
        ((x1,y2),(arm,0)),((x1,y2),(0,-arm)),
        ((x2,y2),(-arm,0)),((x2,y2),(0,-arm)),
    ]:
        cv2.line(frame,(px,py),(px+dx,py+dy),GOLD,2)
    mid_y = (y1+y2)//2
    for ex in [x1,x2]:
        cv2.line(frame,(ex,mid_y-20),(ex,mid_y+20),GOLD_DIM,1)
    header = f"TARGET {pid+1:02d}  |  CONF {conf:.0%}"
    (tw,_),_ = cv2.getTextSize(header,FONT,0.42,1)
    cv2.rectangle(frame,(x1,y1-18),(x1+tw+10,y1),GOLD,-1)
    cv2.putText(frame,header,(x1+5,y1-4),FONT,0.42,(0,0,0),1)
    cv2.putText(frame,f"H:{y2-y1}px",(x1+4,y2+14),FONT,0.38,GOLD_DIM,1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  LIGHTNING OUTLINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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


def draw_lightning_outline(frame, hull):
    """hull is a numpy array or None — never use `or` on it."""
    if hull is None or len(hull) < 3:
        return
    if random.random() < 0.20:   # strobe flicker
        return

    pts = [tuple(p[0]) for p in hull]
    n   = len(pts)

    for i in range(n):
        p1 = pts[i];  p2 = pts[(i+1) % n]
        for strand in range(2):
            amp  = 14 if strand == 0 else 6
            segs = random.randint(5, 10)
            path = zigzag_between(p1, p2, amplitude=amp, segments=segs)
            for j in range(len(path)-1):
                a, b = path[j], path[j+1]
                col  = ELEC_BLUE if strand == 0 else ELEC_PURPLE
                cv2.line(frame, a, b, col, 4 if strand==0 else 2)
                cv2.line(frame, a, b, ELEC_WHITE, 1)

    # random sparks
    for _ in range(random.randint(2, 5)):
        bx, by = random.choice(pts)
        angle  = random.uniform(0, 2*math.pi)
        length = random.uniform(10, 35)
        ex = int(bx + math.cos(angle)*length)
        ey = int(by + math.sin(angle)*length)
        path = zigzag_between((bx,by),(ex,ey), amplitude=6, segments=4)
        for j in range(len(path)-1):
            cv2.line(frame, path[j], path[j+1], ELEC_WHITE, 1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  FIREBALL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def spawn_fire_particles(pool, cx, cy, count=8):
    for _ in range(count):
        pool.append(Particle(cx, cy))
    if len(pool) > 200:
        pool[:] = pool[-200:]


def update_and_draw_fire(frame, pool):
    alive = []
    for p in pool:
        p.life += 1
        if p.life >= p.max_life:
            continue
        p.x  += p.vx;  p.y  += p.vy
        p.vy -= 0.18;  p.vx *= 0.96
        if p.life % 4 == 0:
            p.size = max(1, p.size - 1)
        frac = p.life / p.max_life
        if   frac < 0.15: col = FIRE_WHITE
        elif frac < 0.35: col = FIRE_YELLOW
        elif frac < 0.60: col = FIRE_ORANGE
        elif frac < 0.82: col = FIRE_RED
        else:             col = FIRE_DARK
        cx_, cy_ = int(p.x), int(p.y)
        dim = tuple(max(0, int(c*0.3)) for c in col)
        cv2.circle(frame, (cx_,cy_), p.size+4, dim, -1)
        cv2.circle(frame, (cx_,cy_), p.size,   col, -1)
        alive.append(p)
    pool[:] = alive


def draw_fireball_core(frame, cx, cy, t):
    pulse = int(18 + 6*math.sin(t*8))
    for r, col, alpha in [
        (pulse+14, FIRE_DARK,   0.35),
        (pulse+8,  FIRE_RED,    0.50),
        (pulse+3,  FIRE_ORANGE, 0.65),
        (pulse,    FIRE_YELLOW, 0.80),
        (pulse-6,  FIRE_WHITE,  1.00),
    ]:
        if r <= 0: continue
        ov = frame.copy()
        cv2.circle(ov, (cx,cy), r, col, -1)
        cv2.addWeighted(ov, alpha, frame, 1-alpha, 0, frame)
    cv2.circle(frame, (cx,cy), max(3, pulse-10), FIRE_WHITE, -1)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  BODY SILHOUETTE  (returns hull array or None)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
    cv2.fillConvexPoly(ov, hull, (20, 35, 60))
    cv2.addWeighted(ov, 0.22, frame, 0.78, 0, frame)
    return hull   # numpy array — caller must NOT use `or` on it


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  HUD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def draw_hud_frame(frame, fps, person_count, t):
    h, w = frame.shape[:2]
    elapsed = time.time() - start_time

    for (ox,oy,sx,sy) in [(0,0,1,1),(w,0,-1,1),(0,h,1,-1),(w,h,-1,-1)]:
        cv2.line(frame,(ox,oy),(ox+sx*80,oy),BLUE_CORE,1)
        cv2.line(frame,(ox,oy),(ox,oy+sy*80),BLUE_CORE,1)
        cv2.line(frame,(ox+sx*8,oy+sy*8),(ox+sx*50,oy+sy*8),GOLD,2)
        cv2.line(frame,(ox+sx*8,oy+sy*8),(ox+sx*8,oy+sy*50),GOLD,2)

    title = "STARK INDUSTRIES // THREAT ASSESSMENT SYSTEM"
    (tw,_),_ = cv2.getTextSize(title,FONT,0.62,1)
    tx = (w-tw)//2
    cv2.rectangle(frame,(tx-8,6),(tx+tw+8,34),(0,0,0),-1)
    cv2.putText(frame,title,(tx,28),FONT,0.62,GOLD,1)
    cv2.line(frame,(w//2-400,38),(w//2+400,38),GOLD_DIM,1)

    left_data = [
        ("SYS.TIME",  f"{elapsed:07.2f}s"),
        ("FPS",       f"{fps:05.1f}"),
        ("TARGETS",   f"{person_count:02d}"),
        ("KP.THRESH", f"{KP_CONF:.0%}"),
        ("RES",       "1920x1080"),
        ("MODEL",     "YOLOv8n-POSE"),
        ("STATUS",    "SCANNING"),
        ("POWER.SRC", "ARC REACTOR"),
    ]
    for i,(key,val) in enumerate(left_data):
        y = 70 + i*26
        cv2.putText(frame,key,(14,y),FONT,0.44,BLUE_CORE,1)
        cv2.putText(frame,f": {val}",(130,y),FONT,0.44,WHITE_HUD,1)

    right_data = [
        ("HEART.RATE","-- BPM"),
        ("TEMP",      "-- C"),
        ("THREAT.LVL","LOW"),
        ("ARMOR.MODE","PASSIVE"),
        ("REPULSOR",  "CHARGING"),
        ("FIREBALL",  "ACTIVE"),
        ("LIGHTNING", "ACTIVE"),
    ]
    for i,(key,val) in enumerate(right_data):
        y = 70 + i*26
        cv2.putText(frame,key,(w-260,y),FONT,0.44,BLUE_CORE,1)
        cv2.putText(frame,f": {val}",(w-260+130,y),FONT,0.44,WHITE_HUD,1)

    cv2.rectangle(frame,(0,h-34),(w,h),(0,0,0),-1)
    btxt = (f"  [JARVIS v3.4.1]   FRAME:{frame_count:06d}   "
            f"UPTIME:{elapsed:06.1f}s   VISUAL: ACTIVE   "
            f"FIREBALL: READY   LIGHTNING: ONLINE")
    cv2.putText(frame,btxt,(10,h-10),FONT,0.44,GOLD_DIM,1)

    for cx2,cy2 in [(70,h-70),(w-70,h-70)]:
        draw_arc_reticle(frame,(cx2,cy2),30,GOLD,t)
        glow_circle(frame,(cx2,cy2),6,GOLD,1)
        cv2.circle(frame,(cx2,cy2),2,WHITE_HUD,-1)


def draw_scan_line(frame, scan_y):
    w = frame.shape[1]
    cv2.line(frame,(0,scan_y),(w,scan_y),SCAN_COLOR,1)
    for offset,alpha in [(1,0.4),(3,0.15),(6,0.06)]:
        if scan_y-offset >= 0:
            ov = frame.copy()
            cv2.line(ov,(0,scan_y-offset),(w,scan_y-offset),SCAN_COLOR,1)
            cv2.addWeighted(ov,alpha,frame,1-alpha,0,frame)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  MAIN LOOP
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

cv2.namedWindow("JARVIS // STARK ASSESSMENT SYSTEM", cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty("JARVIS // STARK ASSESSMENT SYSTEM",
                      cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print("JARVIS POSE — Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    t = time.time() - start_time

    ov = np.full(frame.shape, OVERLAY_DARK, dtype=np.uint8)
    frame = cv2.addWeighted(frame, 0.78, ov, 0.22, 0)

    results = model(frame, verbose=False, conf=0.45, device="cuda")[0]

    person_count = 0
    frame_hull   = None   # hull for this frame (numpy array or None)

    if results.keypoints is not None:
        kps_conf_all = results.keypoints.conf

        for idx, person_kps in enumerate(results.keypoints.xy):
            kps   = person_kps.cpu().numpy()
            confs = (kps_conf_all[idx].cpu().numpy()
                     if kps_conf_all is not None else np.ones(len(kps)))
            person_count += 1

            # silhouette — returns numpy array or None
            hull = draw_body_outline(frame, kps, confs)

            # ── safe hull selection (no `or` on arrays!) ───────────────────
            if hull is not None:
                frame_hull = hull
                last_hull  = hull          # persist for next frame
            # use this frame's hull if available, else last known
            active_hull = frame_hull if frame_hull is not None else last_hull

            draw_lightning_outline(frame, active_hull)

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

                if i in (9, 10):   # wrists → FIREBALL
                    pool = fire_particles[i]
                    spawn_fire_particles(pool, cx_, cy_, count=8)
                    draw_fireball_core(frame, cx_, cy_, t + i*3.14)
                    update_and_draw_fire(frame, pool)
                    bracket_box(frame, cx_, cy_, "FIREBALL", FIRE_ORANGE, 16)
                    draw_arc_reticle(frame, cx_, cy_, 30, FIRE_ORANGE, t+i)

                elif i in BOXED_PARTS:
                    label, color, size = BOXED_PARTS[i]
                    bracket_box(frame, cx_, cy_, label, color, size)
                    if i == 0:
                        draw_arc_reticle(frame, cx_, cy_, size+10, color, t+i)
                    glow_circle(frame, (cx_,cy_), 5, color, -1)

                else:
                    glow_circle(frame, (cx_,cy_), 3, TEAL, 1)
                    cv2.circle(frame, (cx_,cy_), 2, TEAL, -1)

    # linger fire particles even without detections
    for pool in fire_particles.values():
        update_and_draw_fire(frame, pool)

    # person boxes
    if results.boxes is not None:
        for pid,box in enumerate(results.boxes):
            conf = float(box.conf[0])
            if conf >= 0.45:
                x1,y1,x2,y2 = map(int,box.xyxy[0])
                draw_person_box(frame,x1,y1,x2,y2,conf,pid)

    # scan sweep
    h_,w_ = frame.shape[:2]
    scan_y = int((t*120) % h_)
    draw_scan_line(frame, scan_y)

    # HUD
    curr_time = time.time()
    fps = 1/max(curr_time-prev_time, 1e-6)
    prev_time = curr_time

    draw_hud_frame(frame, fps, person_count, t)

    cv2.imshow("JARVIS // STARK ASSESSMENT SYSTEM", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
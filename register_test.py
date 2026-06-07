import cv2
import numpy as np
import pickle
import os
import json
from insightface.app import FaceAnalysis

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
)
face_app.prepare(ctx_id=0, det_size=(320, 320))


def augment_image(img):
    augments = [img]
    h, w = img.shape[:2]
    for beta in [-30, -15, 15, 30]:
        augments.append(cv2.convertScaleAbs(img, alpha=1.0, beta=beta))
    for alpha in [0.85, 1.15]:
        augments.append(cv2.convertScaleAbs(img, alpha=alpha, beta=0))
    augments.append(cv2.flip(img, 1))
    margin_x, margin_y = int(w * 0.05), int(h * 0.05)
    cropped = img[margin_y:h-margin_y, margin_x:w-margin_x]
    augments.append(cv2.resize(cropped, (w, h)))
    center = (w // 2, h // 2)
    for angle in [-5, 5]:
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        augments.append(cv2.warpAffine(img, M, (w, h)))
    augments.append(cv2.GaussianBlur(img, (3, 3), 0))
    return augments


def register_student(student_id, image_path, tenant_id):
    img = cv2.imread(image_path)
    if img is None:
        return {"status": "error", "reason": "cannot read image"}

    faces = face_app.get(img)
    if not faces:
        return {"status": "error", "reason": "no face detected"}

    augments = augment_image(img)
    embeddings = []

    for aug in augments:
        faces = face_app.get(aug)
        if not faces:
            continue
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        if face.det_score < 0.4:
            continue
        embeddings.append(face.embedding)

    if not embeddings:
        return {"status": "error", "reason": "no valid embeddings"}

    avg_embedding = np.mean(embeddings, axis=0)
    avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)

    os.makedirs(f"data/embeddings/{tenant_id}", exist_ok=True)
    save_path = f"data/embeddings/{tenant_id}/{student_id}.pkl"
    with open(save_path, "wb") as f:
        pickle.dump({
            "student_id": student_id,
            "tenant_id": tenant_id,
            "embedding": avg_embedding,
            "num_augments": len(embeddings)
        }, f)

    return {"status": "ok", "num_augments": len(embeddings)}


def register_bulk(photos_dir, tenant_id):
    tenant_dir = os.path.join(photos_dir, tenant_id)

    if not os.path.exists(tenant_dir):
        print(f"ERROR: folder {tenant_dir} not found")
        return

    files = [f for f in os.listdir(tenant_dir)
             if f.lower().endswith((".jpg", ".jpeg", ".png"))]

    print(f"Found {len(files)} photos for tenant {tenant_id}\n")
    results = []

    for filename in files:
        student_id = filename.split("_")[0]
        image_path = os.path.join(tenant_dir, filename)

        print(f"Registering {student_id} ({filename})...", end=" ")
        result = register_student(student_id, image_path, tenant_id)

        if result["status"] == "ok":
            print(f"OK — {result['num_augments']} augments")
        else:
            print(f"FAILED — {result['reason']}")

        results.append({"student_id": student_id, **result})

    report_path = f"data/embeddings/{tenant_id}/report.json"
    with open(report_path, "w") as f:
        json.dump(results, f, indent=2)

    success = sum(1 for r in results if r["status"] == "ok")
    print(f"\n── Registration complete ──────────────")
    print(f"Success : {success}/{len(files)}")
    print(f"Report  : {report_path}")


register_bulk("data/student_photos", "TENANT001")
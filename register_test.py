import cv2
import numpy as np
import pickle
from insightface.app import FaceAnalysis

face_app = FaceAnalysis(
    name="buffalo_l",
    providers=["CUDAExecutionProvider", "CPUExecutionProvider"]
)
face_app.prepare(ctx_id=0, det_size=(320, 320))


def augment_image(img):
    """
    Generate multiple augmented versions of one photo.
    Simulates different lighting, slight angles, contrast.
    """
    augments = [img]  # original always included
    h, w = img.shape[:2]

    # slight brightness variations
    for beta in [-30, -15, 15, 30]:
        bright = cv2.convertScaleAbs(img, alpha=1.0, beta=beta)
        augments.append(bright)

    # contrast variations
    for alpha in [0.85, 1.15]:
        contrast = cv2.convertScaleAbs(img, alpha=alpha, beta=0)
        augments.append(contrast)

    # horizontal flip (mirror)
    augments.append(cv2.flip(img, 1))

    # slight zoom in (crop center 90%)
    margin_x = int(w * 0.05)
    margin_y = int(h * 0.05)
    cropped = img[margin_y:h-margin_y, margin_x:w-margin_x]
    augments.append(cv2.resize(cropped, (w, h)))

    # slight rotation -5 and +5 degrees
    center = (w // 2, h // 2)
    for angle in [-5, 5]:
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, M, (w, h))
        augments.append(rotated)

    # gaussian blur (simulates lower quality cam vs sharp ID photo)
    augments.append(cv2.GaussianBlur(img, (3, 3), 0))

    return augments


def register_from_photo(student_id, image_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"ERROR: Cannot read {image_path}")
        return False

    # verify at least one face in original
    faces = face_app.get(img)
    if not faces:
        print(f"ERROR: No face detected in {image_path}")
        return False

    print(f"[OK] Face detected in original photo. Generating augmentations...")

    augments = augment_image(img)
    embeddings = []

    for i, aug in enumerate(augments):
        faces = face_app.get(aug)
        if not faces:
            continue
        face = max(faces, key=lambda f: (f.bbox[2]-f.bbox[0]) * (f.bbox[3]-f.bbox[1]))
        if face.det_score < 0.4:
            continue
        embeddings.append(face.embedding)

    if not embeddings:
        print("ERROR: No valid embeddings from augmentations.")
        return False

    # average + normalize
    avg_embedding = np.mean(embeddings, axis=0)
    avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)

    save_path = f"data/embeddings/{student_id}.pkl"
    with open(save_path, "wb") as f:
        pickle.dump({
            "student_id": student_id,
            "embedding": avg_embedding,
            "num_augments": len(embeddings),
            "source": image_path
        }, f)

    print(f"[OK] Registered {student_id} from {len(embeddings)}/{len(augments)} augmentations.")
    return True


register_from_photo("YUG", "data/student_photos/yug.jpg")
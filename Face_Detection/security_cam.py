import cv2
import numpy as np
import os
from datetime import datetime

# ==============================
# SETTINGS
# ==============================
DATASET_DIR = "dataset"
MODEL_FILE = "face_model.yml"
LABELS_FILE = "labels.npy"
CONF_THRESHOLD = 70            # LBPH confidence (lower is better, try 50-70)
EVENT_COOLDOWN_SEC = 10
SAVE_DIR = "intruder_snapshots"
LOG_FILE = "security_log.csv"

if not os.path.exists(DATASET_DIR):
    os.makedirs(DATASET_DIR)
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Haar Cascade
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)


# ==============================
# IMAGE CAPTURE
# ==============================
def capture_images():
    name = input("Enter person name (folder will be created): ").strip()
    person_dir = os.path.join(DATASET_DIR, name)
    os.makedirs(person_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Capture", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Capture", 800, 600)

    count = 0
    total = 60
    print(f"📸 Capturing {total} images for '{name}'. Look at camera. Press 'q' to stop early.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            roi = cv2.resize(roi, (200, 200))
            file_path = os.path.join(person_dir, f"{count}.jpg")
            cv2.imwrite(file_path, roi)
            count += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 200, 0), 2)

        cv2.imshow("Capture", frame)

        if cv2.waitKey(1) & 0xFF == ord("q") or count >= total:
            break

    cap.release()
    cv2.destroyAllWindows()
    print(f"✅ Saved {count} images to {person_dir}")


# ==============================
# TRAIN MODEL
# ==============================
def train_model():
    faces, labels = [], []
    label_map, current_id = {}, 0

    for person_name in os.listdir(DATASET_DIR):
        person_dir = os.path.join(DATASET_DIR, person_name)
        if not os.path.isdir(person_dir):
            continue

        label_map[current_id] = person_name

        for file in os.listdir(person_dir):
            img_path = os.path.join(person_dir, file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            faces.append(img)
            labels.append(current_id)

        current_id += 1

    if not faces:
        print("⚠️ No data found. Capture images first!")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(labels))
    recognizer.save(MODEL_FILE)
    np.save(LABELS_FILE, label_map)

    print("✅ Model trained and saved.")


# ==============================
# SECURITY CAMERA
# ==============================
def run_security():
    if not os.path.exists(MODEL_FILE) or not os.path.exists(LABELS_FILE):
        print("⚠️ Train the model first!")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(MODEL_FILE)
    label_map = np.load(LABELS_FILE, allow_pickle=True).item()

    cap = cv2.VideoCapture(0)
    cv2.namedWindow("Security Cam", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Security Cam", 800, 600)

    print("🔒 Security Camera ON (press 'q' to quit)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi = gray[y:y+h, x:x+w]
            roi_resized = cv2.resize(roi, (200, 200))

            label_id, confidence = recognizer.predict(roi_resized)

            if confidence <= CONF_THRESHOLD:
                name = label_map.get(label_id, "Unknown")
                color = (0, 200, 0)
                text = f"{name} ({int(confidence)})"
            else:
                name = "Unknown"
                color = (0, 0, 255)
                text = "Unknown"

            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame, text, (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imshow("Security Cam", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("🔓 Security Camera OFF")


# ==============================
# MENU
# ==============================
while True:
    print("\n--- SECURITY SYSTEM ---")
    print("1. Capture Images")
    print("2. Train Model")
    print("3. Run Security Camera")
    print("4. Exit")
    choice = input("\nSelect option: ")

    if choice == "1":
        capture_images()
    elif choice == "2":
        train_model()
    elif choice == "3":
        run_security()
    elif choice == "4":
        print("👋 Exiting...")
        break
    else:
        print("❌ Invalid option.")

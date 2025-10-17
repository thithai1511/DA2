#!/usr/bin/python3
import cv2
import os
from picamera2 import Picamera2

# ==============================
# Nhap MSSV va tao thu muc luu anh
# ==============================
student_id = input("Nhap MSSV: ").strip()
save_path = f"dataset/{student_id}"
os.makedirs(save_path, exist_ok=True)

# ==============================
# Duong dan toi file Haar Cascade
# ==============================
cascade_path = "haarcascade_frontalface_default.xml"
if not os.path.exists(cascade_path):
    print("[ERROR] Khong tim thay file haarcascade. Hay kiem tra lai duong dan!")
    exit(1)

face_detector = cv2.CascadeClassifier(cascade_path)

# ==============================
# Khoi dong camera
# ==============================
cv2.startWindowThread()
picam2 = Picamera2()
picam2.configure(
    picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)})
)
picam2.start()

# ==============================
# Tham so luu anh
# ==============================
count = 0
max_images = 20  # so luong anh muon chup

print(f"[INFO] Bat dau chup anh cho MSSV: {student_id}")
print("[INFO] Tu dong chup khi phat hien khuon mat...")

while True:
    frame = picam2.capture_array()
    grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Phat hien khuon mat
    faces = face_detector.detectMultiScale(grey, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces:
        # Ve khung xanh quanh mat (hien tren anh goc)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cat khuon mat tu anh gray
        face_img = grey[y:y + h, x:x + w]

        # Luu anh khuon mat (dang gray)
        if count < max_images:
            count += 1
            img_path = os.path.join(save_path, f"{student_id}_{count}.jpg")
            cv2.imwrite(img_path, face_img)
            print(f"[INFO] Da luu {img_path}")

        # Neu da du anh thi thoat
        if count >= max_images:
            print(f"[INFO] Hoan thanh: {count} anh da duoc luu trong {save_path}")
            picam2.stop()
            cv2.destroyAllWindows()
            exit(0)

    cv2.imshow("Face Capture", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):  # Nhan 'q' de thoat khan cap
        break

cv2.destroyAllWindows()

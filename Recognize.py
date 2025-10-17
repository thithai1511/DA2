#!/usr/bin/python3
import cv2
import face_recognition
import pickle
from picamera2 import Picamera2


ENCODINGS_PATH = "encodings.pickle"


print("[INFO] Dang load du lieu khuon mat da train ...")
data = pickle.loads(open(ENCODINGS_PATH, "rb").read())

# Khoi tao camera Pi
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(
    main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

while True:
    # Capture frame
    frame = picam2.capture_array()

    # Chuyen sang RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Tim vi tri khuon mat trong frame
    boxes = face_recognition.face_locations(rgb, model="hog")
    encodings = face_recognition.face_encodings(rgb, boxes)

    names = []

    for encoding in encodings:
        matches = face_recognition.compare_faces(data["encodings"], encoding)
        name = "Unknown"

        if True in matches:
            matchedIdxs = [i for (i, b) in enumerate(matches) if b]
            counts = {}

            for i in matchedIdxs:
                name = data["names"][i]
                counts[name] = counts.get(name, 0) + 1

            name = max(counts, key=counts.get)

        names.append(name)

    # Ve khung + MSSV
    for ((top, right, bottom, left), name) in zip(boxes, names):
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, name, (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    cv2.imshow("Nhan dien khuon mat", frame)

    # Bam q de thoat
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()

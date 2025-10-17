#!/usr/bin/python3
# FaceDetect_headless.py - chup anh khuon mat khong GUI, dung cho API
# Dung PiCamera2 -> luu dataset/<mssv>/
# Chay: /usr/bin/python FaceDetect_headless.py --student 22521379 --max 30

import os, sys, argparse, time
import cv2
from picamera2 import Picamera2

def resolve_cascade(name):
    # tim trong thu muc lam viec
    if os.path.isabs(name) and os.path.exists(name): return name
    local = os.path.join(os.getcwd(), name)
    if os.path.exists(local): return local
    # tim trong data cua opencv
    cand = os.path.join(cv2.data.haarcascades, os.path.basename(name))
    if os.path.exists(cand): return cand
    return ""

ap = argparse.ArgumentParser()
ap.add_argument("--student","-s", required=True, help="MSSV")
ap.add_argument("--max", type=int, default=30, help="So anh muon chup")
ap.add_argument("--timeout", type=int, default=30, help="Dung sau N giay neu chua du")
ap.add_argument("--cascade", type=str, default="haarcascade_frontalface_default.xml")
args = ap.parse_args()

student_id = args.student.strip()
save_dir = os.path.join("dataset", student_id)
os.makedirs(save_dir, exist_ok=True)

cpath = resolve_cascade(args.cascade)
if not cpath:
    print("[ERROR] Khong tim thay cascade:", args.cascade, file=sys.stderr)
    sys.exit(2)
det = cv2.CascadeClassifier(cpath)
if det.empty():
    print("[ERROR] Cascade empty:", cpath, file=sys.stderr)
    sys.exit(2)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format":"XRGB8888","size":(640,480)}))
picam2.start()

count = 0
t0 = time.time()
while count < args.max and (time.time() - t0) < args.timeout:
    frame = picam2.capture_array()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = det.detectMultiScale(gray, 1.1, 5, minSize=(80,80))
    for (x,y,w,h) in faces:
        roi = gray[y:y+h, x:x+w]
        if roi.size == 0: continue
        count += 1
        cv2.imwrite(os.path.join(save_dir, f"{student_id}_{count}.jpg"), roi)
        if count >= args.max: break

picam2.stop()
print(f"[INFO] Saved {count} images -> {save_dir}")
sys.exit(0 if count>0 else 1)

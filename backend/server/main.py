# FastAPI backend cho web test (headless)
import os, pathlib, subprocess
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.routing import APIRoute
from fastapi.responses import Response
import cv2
from fastapi.responses import StreamingResponse
from picamera2 import Picamera2
import threading
import time

app = FastAPI(title="Pi5 Face Attendance (Web Test)")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

ROOT = pathlib.Path(__file__).resolve().parents[1]   # ~/DA2-main/backend -> parents[1]=~/DA2-main
PY = "/usr/bin/python3"                              # dung python he thong (picamera2 ok)

@app.get("/api/health")
def health(): return {"ok": True}

# Students & Attendance mau de FE xem UI
@app.get("/api/students")
def list_students():
    return {"items":[
        {"student_id":"22521379","full_name":"Nguyen Van A","class_name":"CE2025-1","email":"a@example.com"},
        {"student_id":"22521449","full_name":"Tran Thi B","class_name":"CE2025-1","email":"b@example.com"}
    ]}

@app.get("/api/attendance")
def attendance():
    return {"items":[
        {"student_id":"22521379","full_name":"Nguyen Van A","recognized_at":"2025-10-15T09:01:02","device_id":"pi5-cam-01"},
        {"student_id":"22521449","full_name":"Tran Thi B","recognized_at":"2025-10-15T09:05:42","device_id":"pi5-cam-01"},
    ]}

class CaptureReq(BaseModel):
    student_id: str
    max_images: int | None = 30

def run_capture(student_id: str, max_images: int):
    script = ROOT / "backend" / "FaceDetect_headless.py"
    # dam bao co cascade (neu file goc co san trong backend/)
    env = os.environ.copy()
    cmd = [PY, str(script), "--student", student_id, "--max", str(max_images)]
    subprocess.run(cmd, cwd=str(ROOT), env=env, check=False)

@app.post("/api/capture")
def api_capture(body: CaptureReq, bg: BackgroundTasks):
    bg.add_task(run_capture, body.student_id, body.max_images or 30)
    return {"ok": True, "queued": True}

def run_train():
    script = ROOT / "Train.py"
    subprocess.run([PY, str(script)], cwd=str(ROOT), check=False)

@app.post("/api/train")
def api_train(bg: BackgroundTasks):
    bg.add_task(run_train)
    return {"ok": True, "queued": True}

# placeholder stream 1x1 de UI khong loi
@app.get("/api/stream")
def stream_placeholder():
    data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc`\x00\x00\x00\x02\x00\x01\xb5\x1d\xde\x7f\x00\x00\x00\x00IEND\xaeB`\x82'
    return Response(content=data, media_type="image/png")

@app.get("/")
def root_info():
    return {"running_from": __file__, "routes": [r.path for r in app.routes if isinstance(r, APIRoute)]}
# --- GLOBAL camera singleton cho stream ---
_stream_lock = threading.Lock()
_stream_picam2 = None
_stream_running = False

def _open_stream_cam():
    global _stream_picam2, _stream_running
    if _stream_picam2 is None:
        _stream_picam2 = Picamera2()
        # video configuration on 640x480 la nhe nhat
        _stream_picam2.configure(
            _stream_picam2.create_video_configuration(
                main={"format": "XRGB8888", "size": (640, 480)}
            )
        )
        _stream_picam2.start()
        _stream_running = True

def _close_stream_cam():
    global _stream_picam2, _stream_running
    if _stream_picam2 is not None:
        try:
            _stream_picam2.stop()
        except Exception:
            pass
        _stream_picam2 = None
    _stream_running = False

def _mjpeg_gen():
    """
    Generator tra ve cac frame JPEG cho StreamingResponse.
    Luu y: neu camera dang bi quy trinh khac giu (vi du capture/train),
    ta co the bi loi open; luc do tra ve 204/503 tuy ban muon.
    """
    with _stream_lock:
        _open_stream_cam()
    try:
        while True:
            frame = _stream_picam2.capture_array()
            # neu can, co the quay frame cho dung mau: frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            ok, jpg = cv2.imencode(".jpg", frame)
            if not ok:
                time.sleep(0.02)
                continue
            buf = jpg.tobytes()
            # multipart boundary la "frame"
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + buf + b"\r\n")
            # ~25fps
            time.sleep(0.04)
    finally:
        # khong dong camera ngay lap tuc de cho phep reload nhanh.
        # Neu muon giai phong ngay, goi _close_stream_cam() o day.
        pass

@app.get("/api/stream")
def api_stream():
    """
    Trinh duyet hien thi bang <img src="/api/stream"> se thay live preview.
    """
    return StreamingResponse(_mjpeg_gen(),
                             media_type="multipart/x-mixed-replace; boundary=frame")

# detect_face_haar.py
# Ghi chu: khong dau de de dang copy vao terminal / VSCode

import cv2
import numpy as np

# Ten file cascade (dat chung thu muc voi script)
FRONTAL = __import__("os").environ.get("HAAR_FRONTAL", "haarcascade_frontalface_default.xml")
PROFILE = __import__("os").environ.get("HAAR_PROFILE", "haarcascade_profileface.xml")
# Bo nho model cascade (lazy load)
_frontal = None
_profile = None

def _load(cascade_name: str) -> cv2.CascadeClassifier:
    """Tai cascade; nem loi neu thieu file."""
    c = cv2.CascadeClassifier(cascade_name)
    if c.empty():
        raise FileNotFoundError(f"Missing cascade: {cascade_name}")
    return c

def _detect_with_threshold(
    cascade: cv2.CascadeClassifier,
    gray: np.ndarray,
    scale: float,
    neighbors: int,
    min_size: int,
    score_th: float | None,
):
    params = dict(
        scaleFactor=scale,
        minNeighbors=neighbors,
        minSize=(min_size, min_size),
    )
    use_threshold = (
        score_th is not None and score_th >= 0 and hasattr(cascade, "detectMultiScale3")
    )
    if use_threshold:
        try:
            rects, reject_levels, level_weights = cascade.detectMultiScale3(
                gray,
                **params,
                outputRejectLevels=True,
            )
            if len(rects) and score_th is not None:
                weights = np.array(level_weights).reshape(-1)
                mask = weights >= score_th
                rects = rects[mask]
            return rects
        except cv2.error:
            # Fallback neu build OpenCV khong ho tro detectMultiScale3
            pass
    return cascade.detectMultiScale(gray, **params)


def detect_boxes(
    gray: np.ndarray,
    scale: float = 1.05,
    neighbors: int = 6,
    min_size: int = 120,
    use_profile: bool = True,
    scale_factor: float | None = None,
    min_neighbors: int | None = None,
    score_th: float | None = None,
) -> list[tuple[int, int, int, int]]:
    """
    Phat hien khuon mat tren anh GRAY.
    Tra ve list (x, y, w, h) int.
    - scale: scaleFactor cua Haar
    - neighbors: minNeighbors
    - min_size: kich thuoc toi thieu (px)
    - use_profile: co dung profileface + flip hay khong
    """
    global _frontal, _profile
    if scale_factor is not None:
        scale = scale_factor
    if min_neighbors is not None:
        neighbors = min_neighbors
    if _frontal is None:
        _frontal = _load(FRONTAL)
    if use_profile and _profile is None:
        _profile = _load(PROFILE)

    boxes: list[tuple[int, int, int, int]] = []

    fb = _detect_with_threshold(_frontal, gray, scale, neighbors, min_size, score_th)
    boxes.extend(list(map(tuple, fb)))

    if use_profile:
        # phat hien nghieng trai
        pb = _detect_with_threshold(_profile, gray, scale, neighbors, min_size, score_th)
        boxes.extend(list(map(tuple, pb)))

        # phat hien nghieng phai bang flip
        gray_flip = cv2.flip(gray, 1)
        pf = _detect_with_threshold(_profile, gray_flip, scale, neighbors, min_size, score_th)
        if len(pf) > 0:
            W = gray.shape[1]
            # chuyen toa do tu anh flip ve anh goc
            pf2 = [(W - x - w, y, w, h) for (x, y, w, h) in pf]
            boxes.extend(pf2)

    # gop cac box overlap de giam trung lap
    boxes = _merge_overlap(boxes, iou_th=0.30)
    return boxes

def _merge_overlap(boxes, iou_th=0.30):
    """NMS don gian bang IOU de gop box trung nhau."""
    if not boxes or len(boxes) == 1:
        return list(map(tuple, boxes))

    b = np.array(boxes, dtype=float)
    x1, y1 = b[:, 0], b[:, 1]
    x2, y2 = b[:, 0] + b[:, 2], b[:, 1] + b[:, 3]
    area = b[:, 2] * b[:, 3]

    idxs = np.argsort(y2)  # sort theo day box
    keep = []
    while len(idxs) > 0:
        i = idxs[-1]
        keep.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:-1]])
        yy1 = np.maximum(y1[i], y1[idxs[:-1]])
        xx2 = np.minimum(x2[i], x2[idxs[:-1]])
        yy2 = np.minimum(y2[i], y2[idxs[:-1]])

        w = np.maximum(0, xx2 - xx1)
        h = np.maximum(0, yy2 - yy1)
        inter = w * h
        iou = inter / (area[i] + area[idxs[:-1]] - inter + 1e-6)

        idxs = idxs[np.where(iou < iou_th)[0]]
    return [tuple(map(int, b[k])) for k in keep]

def expand_to_square(xywh, img_w, img_h, margin=0.35):
    """
    Mo rong box ve hinh vuong, them le margin (ti le).
    Day box xuong duoi chut de om ca cam.
    Clamp trong khung anh.
    """
    x, y, w, h = map(float, xywh)
    s = max(w, h)
    cx = x + w / 2.0
    cy = y + h / 2.0

    s = s * (1.0 + margin)   # tang kich thuoc
    cy = cy + 0.08 * s       # day xuong de gom cam

    x = cx - s / 2.0
    y = cy - s / 2.0

    # clamp
    x = max(0, min(x, img_w - s))
    y = max(0, min(y, img_h - s))
    s = min(s, img_w - x, img_h - y)

    return tuple(map(int, (x, y, s, s)))

# Bo nho box de smoothing
_last_box = None
ALPHA = 0.6  # 0..1, cang cao cang bam theo box moi (it muot hon)

def reset_smooth_box():
    """Reset trang thai smoothing (nen goi moi khi xu ly luong moi)."""
    global _last_box
    _last_box = None

def smooth_box(box):
    """EMA smoothing cho box."""
    global _last_box
    if _last_box is None:
        _last_box = np.array(box, dtype=float)
    else:
        _last_box = ALPHA * np.array(box, dtype=float) + (1.0 - ALPHA) * _last_box
    return tuple(map(int, _last_box))

def crop_face_bgr(
    img_bgr: np.ndarray,
    box: tuple[int, int, int, int] | None = None,
    margin: float = 0.35,
    expand: float | None = None,
    out_size: int = 112,
    smooth: bool = False,
    **kw,
):
    """
    Cat khuon mat tu anh BGR.
    - Neu box None -> tu detect bang detect_boxes(gray, **kw)
    - Tra ve (face_bgr, box_used). box_used da duoc mo rong + vuong hoa + smooth.
    """
    H, W = img_bgr.shape[:2]

    if box is None:
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        boxes = detect_boxes(gray, **kw)
        if not boxes:
            return None, None
        # chon box co dien tich lon nhat
        box = max(boxes, key=lambda b: b[2] * b[3])

    eff_margin = margin if expand is None else expand
    bx = expand_to_square(box, W, H, margin=eff_margin)
    if smooth:
        bx = smooth_box(bx)

    x, y, s, _ = bx
    face = img_bgr[y : y + s, x : x + s].copy()
    if face.size == 0:
        return None, None

    face = cv2.resize(face, (out_size, out_size), interpolation=cv2.INTER_LINEAR)
    return face, bx

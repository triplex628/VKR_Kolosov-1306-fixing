# server/routes/stream.py
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import jwt, JWTError
import cv2, base64, json, math, numpy as np

from server.ml.processor import PoseProcessor
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter()
processor = PoseProcessor()

ANGLE_THRESHOLD = 10
MIN_VIS = 0.6

# ── helpers ──────────────────────────────────────────────────
def avg(p1, p2):
    return {"x": (p1["x"]+p2["x"])/2,
            "y": (p1["y"]+p2["y"])/2,
            "z": (p1["z"]+p2["z"])/2}

def vec_angle(u, v):
    dot = u[0]*v[0] + u[1]*v[1]
    nu  = (u[0]**2 + u[1]**2) ** .5
    nv  = (v[0]**2 + v[1]**2) ** .5
    if nu == 0 or nv == 0: return 0
    cos_t = max(-1, min(1, dot / (nu*nv)))
    return math.degrees(math.acos(cos_t))

def bad_points(user, ref):
    bad = []
    ku  = user["landmarks"]
    kr  = ref["landmarks"]

    if len(ku) < 25 or len(kr) < 25:
        return list(range(len(ku)))         # Mediapipe «промазал»

    cu_sh = avg(ku[11], ku[12])
    cr_sh = avg(kr[11], kr[12])
    cu_hp = avg(ku[23], ku[24])
    cr_hp = avg(kr[23], kr[24])

    for i in range(len(ku)):
        if i >= len(kr): continue
        if ku[i]["visibility"] < MIN_VIS or kr[i]["visibility"] < MIN_VIS:
            continue
        cu = cu_sh if i < 23 else cu_hp
        cr = cr_sh if i < 23 else cr_hp
        u  = (ku[i]["x"]-cu["x"], ku[i]["y"]-cu["y"])
        v  = (kr[i]["x"]-cr["x"], kr[i]["y"]-cr["y"])
        if vec_angle(u, v) > ANGLE_THRESHOLD:
            bad.append(i)
    return bad

# ── websocket ────────────────────────────────────────────────
@router.websocket("/ws/stream")
async def stream(ws: WebSocket):
    """Получает jpeg-кадры, отдаёт оценку позы."""
    token = ws.query_params.get("token")
    if not token:
        return await ws.close(code=status.WS_1008_POLICY_VIOLATION)
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return await ws.close(code=status.WS_1008_POLICY_VIOLATION)

    await ws.accept()
    reference = None

    try:
        while True:
            try:
                msg = json.loads(await ws.receive_text())
            except WebSocketDisconnect:
                break

            # ---------- выбор эталона ----------
            if msg.get("type") == "pose":
                key = msg.get("poseName")
                reference = processor.load_reference(
                    f"server/ml/reference_images/{key}.png"
                )
                await ws.send_text('{"status":"reference set"}')
                continue
            if reference is None:
                await ws.send_text('{"error":"no_reference"}')
                continue

            # ---------- декод кадра ----------
            try:
                _, b64 = msg["image"].split(",", 1)
                arr    = np.frombuffer(base64.b64decode(b64), np.uint8)
                frame  = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            except Exception:
                await ws.send_text('{"error":"bad_frame"}')
                continue
            if frame is None: continue

            current = processor.process_frame(frame)

            # если Mediapipe не нашёл всех точек — score 0, чтобы не ронять сокет
            if len(current["landmarks"]) < 29:
                await ws.send_text(json.dumps({
                    "score": 0,
                    "bad_points": [],
                    "good_points": [],
                    "landmarks": current["landmarks"],
                    "connections": current["connections"]
                }))
                continue

            bad = bad_points(current, reference)
            good = [i for i in range(len(current["landmarks"])) if i not in bad]
            total = len(bad) + len(good)
            score = int(100 * len(good) / total) if total else 0

            ankles_ok = (
                current["landmarks"][27]["visibility"] > 0.4 and
                current["landmarks"][28]["visibility"] > 0.4
            )
            if not ankles_ok:
                score = max(score - 40, 0)

            await ws.send_text(json.dumps({
                "score": score,
                "bad_points": bad,
                "good_points": good,
                "landmarks": current["landmarks"],
                "connections": current["connections"]
            }))

    except WebSocketDisconnect:
        pass

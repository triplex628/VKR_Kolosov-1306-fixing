# server/routes/stream.py
# --------------------------------------------------------------------------- #
# Веб-сокет-роут: получает кадры с фронта, сравнивает позу с эталонной и
# возвращает оценку + списки «хороших / плохих» key-points.
# --------------------------------------------------------------------------- #

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt
import json, base64, cv2, numpy as np, math

from server.ml.processor import PoseProcessor
from ..auth import SECRET_KEY, ALGORITHM

router = APIRouter()
processor = PoseProcessor()

# ===================== НАСТРОЙКИ МЕТРИКИ ===================================== #
ANGLE_THRESHOLD = 10        # допуск по углу (°) между векторами «центр-точка»
MIN_VISIBILITY  = 0.6       # игнорируем точки, хуже распознанные MediaPipe

# Если фронт шлёт poseId вместо poseName — раскомментируйте и заполните:
# POSE_MAP = {
#     1: "downward_dog",
#     2: "chair",
#     3: "triangle",
#     4: "plank",
#     5: "warrior2",
#     6: "extended_angle",
# }
# ============================================================================ #


# ------------------------- ВСПОМОГАТЕЛЬНЫЕ ---------------------------------- #
def average_point(p1: dict, p2: dict) -> dict:
    """Середина сегмента (используем для центра плеч и таза)."""
    return {
        "x": (p1["x"] + p2["x"]) / 2,
        "y": (p1["y"] + p2["y"]) / 2,
        "z": (p1["z"] + p2["z"]) / 2,
    }


def vector_angle(u: tuple, v: tuple) -> float:
    """Возвращает угол между векторами u и v (2-D) в градусах."""
    dot = u[0] * v[0] + u[1] * v[1]
    norm_u = (u[0] ** 2 + u[1] ** 2) ** 0.5
    norm_v = (v[0] ** 2 + v[1] ** 2) ** 0.5
    if norm_u == 0 or norm_v == 0:
        return 0
    cos_theta = max(-1, min(1, dot / (norm_u * norm_v)))
    return math.degrees(math.acos(cos_theta))


def compare_poses_by_angle_vector(
    user_pose: dict,
    ref_pose: dict,
    threshold: float = ANGLE_THRESHOLD,
) -> list[int]:
    """
    Отметка «плохих» точек:
    • строим векторы (центр → точка) у пользователя и эталона;
    • считаем угол между ними;
    • если угол > threshold — точка считается неверной.
    """
    bad_points: list[int] = []
    keypoints = user_pose["landmarks"]
    refpoints = ref_pose["landmarks"]

    # На всякий случай проверка длины (MediaPipe = 33 key-points)
    if len(keypoints) < 25 or len(refpoints) < 25:
        return list(range(len(keypoints)))

    # центры: середины плеч (11,12) и бёдер (23,24)
    c12_user = average_point(keypoints[11], keypoints[12])
    c34_user = average_point(keypoints[23], keypoints[24])
    c12_ref  = average_point(refpoints[11], refpoints[12])
    c34_ref  = average_point(refpoints[23], refpoints[24])

    for idx in range(len(keypoints)):
        if idx >= len(refpoints):
            continue

        # пропускаем шумные или «невидимые» точки
        if (
            keypoints[idx]["visibility"] < MIN_VISIBILITY or
            refpoints[idx]["visibility"] < MIN_VISIBILITY
        ):
            continue

        center_user = c12_user if idx < 23 else c34_user
        center_ref  = c12_ref  if idx < 23 else c34_ref

        u = (
            keypoints[idx]["x"] - center_user["x"],
            keypoints[idx]["y"] - center_user["y"],
        )
        v = (
            refpoints[idx]["x"] - center_ref["x"],
            refpoints[idx]["y"] - center_ref["y"],
        )

        if vector_angle(u, v) > threshold:
            bad_points.append(idx)

    return bad_points
# --------------------------------------------------------------------------- #


# --------------------------- ГЛАВНЫЙ ВЕБ-СОКЕТ ------------------------------ #
@router.websocket("/ws/stream")
async def stream_pose(ws: WebSocket):
    """
    • Кадр приходит от фронта base64-строкой «data:image/jpeg;base64,...».
    • Перед началом клиент шлёт {type:"pose", poseName:"chair"} — мы
      подгружаем эталонное изображение.
    • В ответ отправляем JSON с полями: score, bad_points, good_points,
      landmarks, connections.
    """
    # ---- Аутентификация JWT из query-string -------------------------------- #
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("sub"):  # e-mail в токене
            raise JWTError()
    except JWTError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws.accept()
    reference_pose: dict | None = None  # будет хранить эталон

    try:
        while True:
            raw = await ws.receive_text()
            msg = json.loads(raw)

            # ---------- Выбор/смена позы клиентом --------------------------- #
            if msg.get("type") == "pose":
                pose_key: str | None = msg.get("poseName")
                if not pose_key:
                    pose_id = msg.get("poseId")
                    # pose_key = POSE_MAP.get(pose_id) if pose_id else None
                    if pose_id is not None and pose_key is None:
                        await ws.send_text(json.dumps({"error": "unknown_pose"}))
                        continue

                reference_pose = processor.load_reference(
                    f"server/ml/reference_images/{pose_key}.png"
                )
                await ws.send_text(json.dumps({"status": "reference set"}))
                continue  # ждём следующего сообщения

            # Если эталон не загружен — сразу отвечаем ошибкой
            if reference_pose is None:
                await ws.send_text(json.dumps({"error": "no_reference"}))
                continue

            # ---------- Декодирование кадра -------------------------------- #
            try:
                header, b64 = msg["image"].split(",", 1)
                img_data = base64.b64decode(b64)
                arr = np.frombuffer(img_data, np.uint8)
                frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            except Exception:
                frame = None

            if frame is None:
                await ws.send_text(json.dumps({"error": "bad_frame"}))
                continue

            # ---------- Обработка кадра и вычисление метрики --------------- #
            current_pose = processor.process_frame(frame)

            bad_points = compare_poses_by_angle_vector(
                current_pose, reference_pose
            )
            good_points = [
                i
                for i in range(len(current_pose["landmarks"]))
                if i not in bad_points
            ]

            total = len(bad_points) + len(good_points)
            score = int(100 * len(good_points) / total) if total else 0
            score = max(0, min(score, 100))  # «клипуем» значение

            await ws.send_text(json.dumps({
                "score":       score,
                "bad_points":  bad_points,
                "good_points": good_points,
                "landmarks":   current_pose["landmarks"],
                "connections": current_pose["connections"],
            }))

    except WebSocketDisconnect:
        # клиент сам закрыл сокет
        pass

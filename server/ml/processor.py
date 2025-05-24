import cv2
import mediapipe as mp
import numpy as np

class PoseProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.POSE_CONNECTIONS = self.mp_pose.POSE_CONNECTIONS
        self.LandmarkEnum = self.mp_pose.PoseLandmark

    def process_frame(self, frame: np.ndarray) -> dict:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.pose.process(rgb)

        output = {"landmarks": [], "connections": []}

        if res.pose_landmarks:
            for lm in res.pose_landmarks.landmark:
                output["landmarks"].append({
                    "x": lm.x,
                    "y": lm.y,
                    "z": lm.z,
                    "visibility": lm.visibility
                })

            output["connections"] = [(i, j) for i, j in self.POSE_CONNECTIONS]
        else:
            # ⛔ Для отладки — сохранить кадр, где поза не найдена
            cv2.imwrite("no_pose_frame.jpg", frame)
            print("⚠️ Позы не распознаны.")

        return output

    def load_reference(self, path: str) -> dict:
        img = cv2.imread(path)
        if img is None:
            print(f"⚠️ Не удалось загрузить эталон: {path}")
            return {"landmarks": [], "connections": []}
        return self.process_frame(img)

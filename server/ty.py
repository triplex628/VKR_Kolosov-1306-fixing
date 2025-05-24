import mediapipe as mp
from mediapipe.python.solutions.pose import PoseLandmark
print("OK:", mp.__version__, PoseLandmark.RIGHT_SHOULDER.name)
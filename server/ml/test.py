import cv2
import sys
import os
sys.path.append(os.path.abspath('.'))
import cv2
from server.ml.processor import PoseProcessor
from server.routers.stream import compare_poses_by_angle_vector

# === Настройки ===
TEST_IMAGE_PATH = "server/ml/reference_images/yoga1.png"
REFERENCE_IMAGE_PATH = "server/ml/reference_images/yoga1.png"
THRESHOLD = 20
IGNORE_POINTS = {0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 21, 22}  # глаза, уши, пальцы

# === Зоны тела для анализа ===
ZONES = {
    "руки": [11, 13, 15, 17, 19, 12, 14, 16, 18, 20],
    "ноги": [23, 25, 27, 29, 31, 24, 26, 28, 30, 32],
    "туловище": [8, 11, 12, 23, 24, 26],
}

# === Подключение модели ===
processor = PoseProcessor()
ref_img = cv2.imread(REFERENCE_IMAGE_PATH)
test_img = cv2.imread(TEST_IMAGE_PATH)

if ref_img is None or test_img is None:
    raise FileNotFoundError("Проверь путь к изображениям!")

ref_pose = processor.process_frame(ref_img)
test_pose = processor.process_frame(test_img)

# === Сравнение ===
bad_points = compare_poses_by_angle_vector(test_pose, ref_pose, threshold=THRESHOLD)
bad_points = [i for i in bad_points if i not in IGNORE_POINTS]
good_points = [i for i in range(len(test_pose["landmarks"])) if i not in bad_points and i not in IGNORE_POINTS]

# === Подсчёт точности по зонам ===
zone_scores = {}
for name, points in ZONES.items():
    points = [i for i in points if i not in IGNORE_POINTS]
    if not points:
        continue
    bad = sum(1 for p in points if p in bad_points)
    total = len(points)
    score = round(100 * (1 - bad / total))
    zone_scores[name] = score

# === Отображение результата ===
for idx in bad_points:
    pt = test_pose["landmarks"][idx]
    x = int(pt["x"] * test_img.shape[1])
    y = int(pt["y"] * test_img.shape[0])
    cv2.circle(test_img, (x, y), 5, (0, 0, 255), -1)

for idx in good_points:
    pt = test_pose["landmarks"][idx]
    x = int(pt["x"] * test_img.shape[1])
    y = int(pt["y"] * test_img.shape[0])
    cv2.circle(test_img, (x, y), 5, (0, 255, 0), -1)

# === Вывод в консоль ===
print(f"\nОбщих 'плохих' точек: {len(bad_points)}")
print("Ошибки в точках:", bad_points)
print("\nОценка по зонам:")
for zone, score in zone_scores.items():
    print(f"  {zone}: {score}%")

# === Показ изображения ===
cv2.imshow("Result", test_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

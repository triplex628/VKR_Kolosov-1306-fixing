# server/routes/ml.py
from fastapi import APIRouter, File, UploadFile, HTTPException
import numpy as np
import cv2

from server.ml.processor import PoseProcessor
from server.schemas import PoseProcessResponse

router = APIRouter()
processor = PoseProcessor()

@router.post("/process-pose", response_model=PoseProcessResponse)
async def process_pose(file: UploadFile = File(...)):
    data = await file.read()
    arr = np.frombuffer(data, np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None:
        raise HTTPException(status_code=400, detail="Не удалось декодировать изображение")
    result = processor.process_frame(frame)
    return result

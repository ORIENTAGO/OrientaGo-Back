import time
import cv2
import numpy as np
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.schemas.detection import DetectionResponse
from app.core.detector import run_inference

router = APIRouter()

@router.post("/detect", response_model=DetectionResponse)
async def detect(frame: UploadFile = File(...)):
    contents = await frame.read()
    np_arr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if image is None:
        raise HTTPException(status_code=400, detail="No se pudo decodificar la imagen")

    start = time.time()
    detections = run_inference(image)
    elapsed_ms = round((time.time() - start) * 1000, 1)

    return DetectionResponse(detections=detections, inference_ms=elapsed_ms)

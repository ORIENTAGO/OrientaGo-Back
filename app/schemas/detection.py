from typing import List
from pydantic import BaseModel

class Detection(BaseModel):
    label: str
    confidence: float
    distancia_aprox_m: float
    bbox: List[float]  # x1, y1, x2, y2 (normalizado 0-1)
    en_trayectoria: bool  # True si el objeto invade el carril central del peatón

class DetectionResponse(BaseModel):
    detections: List[Detection]
    inference_ms: float

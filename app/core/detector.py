import io
import os
import cv2
import numpy as np
import onnxruntime as ort
from typing import List
from fastapi import HTTPException
from app.config import (
    MODEL_PATH, INPUT_SIZE, CONF_THRESHOLD, NMS_THRESHOLD,
    RELEVANT_CLASSES, REFERENCE_HEIGHTS_M, DEFAULT_HEIGHT_M
)
from app.schemas.detection import Detection

_session: ort.InferenceSession | None = None

def get_session() -> ort.InferenceSession:
    global _session
    if _session is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(
                status_code=500,
                detail=(
                    f"No se encontró el modelo en {MODEL_PATH}. "
                    "Descarga/exporta yolov8n.onnx y colócalo en models/."
                ),
            )
        _session = ort.InferenceSession(
            MODEL_PATH, providers=["CPUExecutionProvider"]
        )
    return _session

def letterbox(image: np.ndarray, new_size: int = INPUT_SIZE):
    h, w = image.shape[:2]
    scale = min(new_size / h, new_size / w)
    nh, nw = int(round(h * scale)), int(round(w * scale))
    resized = cv2.resize(image, (nw, nh))
    canvas = np.full((new_size, new_size, 3), 114, dtype=np.uint8)
    top = (new_size - nh) // 2
    left = (new_size - nw) // 2
    canvas[top : top + nh, left : left + nw] = resized
    return canvas, scale, left, top

def estimate_distance_m(bbox_height_px: float, image_height_px: int, class_id: int) -> float:
    """
    Estimación aproximada de distancia a partir del tamaño relativo del
    objeto en la imagen y su altura real de referencia.
    """
    relative_height = float(bbox_height_px) / float(image_height_px)
    if relative_height <= 0:
        return 99.0
    altura_real = REFERENCE_HEIGHTS_M.get(class_id, DEFAULT_HEIGHT_M)
    distancia = altura_real / (relative_height * 1.4)
    return round(min(float(distancia), 20.0), 1)

def run_inference(image: np.ndarray) -> List[Detection]:
    session = get_session()
    img_h, img_w = image.shape[:2]

    canvas, scale, pad_left, pad_top = letterbox(image, INPUT_SIZE)
    blob = canvas.astype(np.float32) / 255.0
    blob = blob.transpose(2, 0, 1)[None, ...]

    input_name = session.get_inputs()[0].name
    outputs = session.run(None, {input_name: blob})
    predictions = outputs[0]

    if predictions.shape[1] < predictions.shape[2]:
        predictions = predictions[0].T
    else:
        predictions = predictions[0]

    boxes, scores, class_ids = [], [], []
    for row in predictions:
        class_scores = row[4:]
        class_id = int(np.argmax(class_scores))
        confidence = float(class_scores[class_id])
        if confidence < CONF_THRESHOLD or class_id not in RELEVANT_CLASSES:
            continue
        cx, cy, w, h = row[0], row[1], row[2], row[3]
        x1 = (cx - w / 2 - pad_left) / scale
        y1 = (cy - h / 2 - pad_top) / scale
        x2 = (cx + w / 2 - pad_left) / scale
        y2 = (cy + h / 2 - pad_top) / scale
        boxes.append([x1, y1, x2 - x1, y2 - y1])
        scores.append(confidence)
        class_ids.append(class_id)

    detections: List[Detection] = []
    if boxes:
        indices = cv2.dnn.NMSBoxes(boxes, scores, CONF_THRESHOLD, NMS_THRESHOLD)
        for i in np.array(indices).flatten():
            x, y, w, h = boxes[i]
            x1, y1, x2, y2 = x, y, x + w, y + h
            detections.append(
                Detection(
                    label=RELEVANT_CLASSES[class_ids[i]],
                    confidence=round(float(scores[i]), 2),
                    distancia_aprox_m=estimate_distance_m(h, img_h, class_ids[i]),
                    bbox=[
                        round(float(x1) / img_w, 3),
                        round(float(y1) / img_h, 3),
                        round(float(x2) / img_w, 3),
                        round(float(y2) / img_h, 3),
                    ],
                )
            )
    return detections

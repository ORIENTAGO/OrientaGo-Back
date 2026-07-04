import os

# Directorio base del backend (OrientaGo-Back)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta del modelo YOLO ONNX
MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8n.onnx")

# Parámetros de entrada del modelo
INPUT_SIZE = 640
CONF_THRESHOLD = 0.45
NMS_THRESHOLD = 0.45

# Clases COCO relevantes para el MVP (id: nombre en español)
RELEVANT_CLASSES = {
    0: "persona",
    56: "silla",
    57: "sofa",
    60: "mesa",
    13: "banco",
}

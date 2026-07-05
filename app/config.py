import os

# Directorio base del backend (OrientaGo-Back)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Ruta del modelo YOLO ONNX
MODEL_PATH = os.path.join(BASE_DIR, "models", "yolov8n.onnx")

# Parámetros de entrada del modelo
INPUT_SIZE = 640
CONF_THRESHOLD = 0.45
NMS_THRESHOLD = 0.45

# Clases COCO relevantes para un peatón (id: nombre en español)
RELEVANT_CLASSES = {
    0: "persona",
    1: "bicicleta",
    2: "carro",
    3: "motocicleta",
    5: "bus",
    6: "tren",
    7: "camión",
    8: "bote",
    9: "semáforo",
    10: "hidrante",
    11: "señal de alto",
    12: "parquímetro",
    13: "banco",
    14: "ave",
    15: "gato",
    16: "perro",
    17: "caballo",
    18: "oveja",
    19: "vaca",
    24: "mochila",
    25: "paraguas",
    26: "bolso",
    28: "maleta",
    32: "pelota",
    36: "patineta",
    56: "silla",
    57: "sofá",
    58: "maceta",
    60: "mesa",
}

# Altura real aproximada (en metros) de cada categoría para estimar distancia
REFERENCE_HEIGHTS_M = {
    0: 1.65,   # persona
    1: 1.0,    # bicicleta
    2: 1.5,    # carro
    3: 1.2,    # motocicleta
    5: 3.0,    # bus
    6: 3.5,    # tren
    7: 2.5,    # camión
    8: 1.5,    # bote
    9: 3.0,    # semáforo
    10: 0.75,  # hidrante
    11: 2.1,   # señal de alto (con poste)
    12: 1.2,   # parquímetro
    13: 0.9,   # banco
    14: 0.3,   # ave
    15: 0.3,   # gato
    16: 0.5,   # perro
    17: 1.6,   # caballo
    18: 0.8,   # oveja
    19: 1.4,   # vaca
    24: 0.45,  # mochila
    25: 0.9,   # paraguas
    26: 0.3,   # bolso
    28: 0.6,   # maleta
    32: 0.22,  # pelota
    36: 0.15,  # patineta
    56: 0.9,   # silla
    57: 0.85,  # sofá
    58: 0.5,   # maceta
    60: 0.75,  # mesa
}
DEFAULT_HEIGHT_M = 1.0


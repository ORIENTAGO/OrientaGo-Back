# OrientaGo-Back

Este es el backend del proyecto **OrientaGo (Asistente Visual para Personas Ciegas)**. Está estructurado siguiendo un diseño de **Arquitectura en Capas (Layered Architecture)** utilizando el framework **FastAPI**.

## Estructura del Proyecto

La estructura del código sigue el siguiente patrón modular:

```text
OrientaGo-Back/
├── app/
│   ├── api/                    # Capa de Presentación (Controladores / Rutas)
│   │   ├── endpoints/          # Endpoints individuales (health, detection)
│   │   └── router.py           # Agrupador central de routers de la API
│   ├── core/                   # Capa de Lógica de Negocio (Servicios / Algoritmos)
│   │   └── detector.py         # Procesamiento e inferencia con ONNX Runtime (YOLO)
│   ├── schemas/                # Capa de Datos (Esquemas Pydantic / DTOs)
│   │   └── detection.py        # Modelos de entrada y salida
│   ├── config.py               # Variables globales de configuración y constantes
│   └── main.py                 # Instanciación de la aplicación FastAPI y CORS
├── models/
│   └── yolov8n.onnx            # Archivo binario del modelo YOLOv8 en formato ONNX
├── main.py                     # Punto de entrada raíz para compatibilidad
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Esta documentación
```

---

## Cómo Correr el Proyecto

### 1. Requisitos Previos
Asegúrate de tener Python 3.10+ instalado. Se recomienda usar un entorno virtual (`venv`):

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# En Linux/macOS:
source venv/bin/activate
```

### 2. Instalar Dependencias
Instala los paquetes necesarios enumerados en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Modelo YOLOv8 ONNX
Asegúrate de que el modelo `yolov8n.onnx` esté ubicado dentro de la carpeta `models/`. Si no lo tienes, puedes exportarlo ejecutando lo siguiente en una terminal alternativa con `ultralytics` instalado:
```bash
pip install ultralytics
yolo export model=yolov8n.pt format=onnx opset=12
# Luego mueve el archivo resultante 'yolov8n.onnx' a la carpeta 'models/' de este proyecto.
```

### 4. Iniciar el Servidor
Puedes correr el servidor utilizando `uvicorn`. Se mantiene total compatibilidad con el comando original:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## Endpoints Disponibles

* **`GET /health`**: Verifica que el servidor y el modelo ONNX estén cargados correctamente.
* **`POST /detect`**: Recibe un archivo de imagen en formato multipart/form-data (`frame`) y devuelve una lista de detecciones con sus respectivos bounding boxes, confianzas y distancias aproximadas estimadas en metros.
* **Docs de Swagger**: Accede a `http://127.0.0.1:8000/docs` para interactuar con la API directamente desde el navegador.
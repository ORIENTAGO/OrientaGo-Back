# OrientaGo — Backend (Servidor de Detección de Objetos)

Este es el backend del proyecto **OrientaGo (Asistente Visual para Personas Ciegas)**. Está construido en **Python + FastAPI** y estructurado siguiendo un diseño de **Arquitectura en Capas (Layered Architecture)**. 

Recibe fotogramas de la aplicación móvil y utiliza el modelo **YOLOv8n (ONNX)** para detectar personas, vehículos, animales, obstáculos y mobiliario urbano en tiempo real. Además, calcula una distancia estimada para que el frontend pueda emitir alertas por voz al usuario.

Este servicio funciona como el "cerebro" del modo **Analizar Entorno / Caminata** de OrientaGo.

---

## Índice

- [Estructura del Proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Conectar la App Móvil](#conectar-la-app-móvil)
- [Endpoints de la API](#endpoints-de-la-api)
- [Qué detecta el modelo](#qué-detecta-el-modelo)
- [Cómo funciona la estimación de distancia](#cómo-funciona-la-estimación-de-distancia)
- [Configuración y Ajustes](#configuración-y-ajustes)
- [Solución de Problemas](#solución-de-problemas)
- [Limitaciones Conocidas](#limitaciones-conocidas)
- [Roadmap / Próximos Pasos](#roadmap--próximos-pasos)

---

## Estructura del Proyecto

El backend sigue una arquitectura modular en capas para facilitar el mantenimiento y la escalabilidad del sistema:

```text
OrientaGo-Back/
├── app/
│   ├── api/                    # Capa de Presentación (Controladores / Rutas)
│   │   ├── endpoints/          # Endpoints individuales (health, detection)
│   │   │   ├── health.py       # Endpoint GET /health
│   │   │   └── detection.py    # Endpoint POST /detect
│   │   └── router.py           # Agrupador central de routers de la API
│   ├── core/                   # Capa de Lógica de Negocio (Servicios / Algoritmos)
│   │   └── detector.py         # Inferencia con ONNX Runtime y letterboxing
│   ├── schemas/                # Capa de Datos (Esquemas Pydantic / DTOs)
│   │   └── detection.py        # Estructuras de respuesta para JSON
│   ├── config.py               # Configuración global, constantes y clases de YOLO
│   └── main.py                 # Instanciación de la aplicación FastAPI y CORS
├── models/
│   ├── .gitkeep                # Mantiene la carpeta en Git
│   └── yolov8n.onnx            # Archivo binario del modelo YOLOv8
├── main.py                     # Punto de entrada raíz para compatibilidad de uvicorn
├── requirements.txt            # Dependencias del proyecto
└── README.md                   # Esta documentación
```

---

## Requisitos

- **Python 3.9 o superior** (probado y compatible hasta Python 3.13)
- Conexión a internet únicamente para la instalación inicial. (Una vez instalado, el servidor funciona 100% local, sin necesidad de conexión externa).
- ~200 MB de espacio libre en disco.
- No se requiere GPU/tarjeta gráfica: el modelo corre eficientemente sobre CPU utilizando `onnxruntime` (`CPUExecutionProvider`).

---

## Instalación

1. **Clonar el proyecto y navegar a la carpeta**:
   ```bash
   cd OrientaGo-Back
   ```

2. **Crear un entorno virtual (venv)**:
   ```bash
   # En Windows/macOS/Linux:
   python -m venv venv
   ```

3. **Activar el entorno virtual**:
   * **En Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **En Windows (CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * **En macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Descargar el modelo YOLOv8 ONNX (opcional)**:
   El modelo `yolov8n.onnx` ya viene incluido en `models/yolov8n.onnx`. Si no estuviera presente por algún motivo, puedes descargarlo sin necesidad de instalar `ultralytics`/`torch` pesados ejecutando:
   ```bash
   # En Windows (PowerShell):
   New-Item -ItemType Directory -Force -Path models
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/yoobright/yolo-onnx/master/yolov8n.onnx" -OutFile models/yolov8n.onnx

   # En Linux / macOS:
   mkdir -p models
   curl -sL -o models/yolov8n.onnx "https://raw.githubusercontent.com/yoobright/yolo-onnx/master/yolov8n.onnx"
   ```

---

## Ejecución

Para iniciar el servidor, corre el siguiente comando desde la raíz de `OrientaGo-Back`:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Deberías ver una salida en consola confirmando el inicio:
```text
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

> **Nota:** La bandera `--reload` permite que el servidor se reinicie automáticamente si editas y guardas archivos del código.

Para verificar que está funcionando, accede a [http://localhost:8000/health](http://localhost:8000/health) desde tu navegador. Debería responder:
```json
{"status": "ok", "modelo_cargado": true}
```

---

## Conectar la App Móvil

Tanto el teléfono móvil de pruebas como la computadora que aloja este servidor **deben estar conectados a la misma red WiFi**:

1. **Obtener tu IP local**:
   * **Windows**: Abre una terminal, ejecuta `ipconfig` y busca la "Dirección IPv4" del adaptador de LAN inalámbrica (WiFi). Suele ser del estilo `192.168.X.X`.
   * **macOS / Linux**: Ejecuta `ifconfig` o `ip addr`.
2. **Configurar el Frontend**: Abre el código del frontend y coloca esa dirección IP (ejemplo: `http://192.168.1.15:8000`) en la variable de entorno o archivo de configuración `frontend/src/config/env.ts` (en la constante `BACKEND_URL`).
3. **Firewall**: Si tu móvil no logra hacer conexión directa, lo más probable es que el firewall de Windows esté bloqueando la entrada por el puerto 8000. Revisa la sección de [Solución de problemas](#solución-de-problemas).

---

## Endpoints de la API

FastAPI autogenera documentación interactiva Swagger. Puedes verla en [http://localhost:8000/docs](http://localhost:8000/docs).

### `GET /health`
Verifica que el servidor y el modelo estén cargados y listos.

* **Respuesta (`200 OK`)**:
  ```json
  {
    "status": "ok",
    "modelo_cargado": true
  }
  ```

### `POST /detect`
Recibe una imagen a través de `multipart/form-data` y retorna la lista de objetos detectados junto con su distancia estimada.

* **Request**: Multipart form con un campo de tipo archivo llamado `frame` conteniendo una imagen (JPEG/PNG).
* **Ejemplo con cURL**:
  ```bash
  curl -X POST http://localhost:8000/detect -F "frame=@foto.jpg"
  ```
* **Respuesta (`200 OK`)**:
  ```json
  {
    "detections": [
      {
        "label": "persona",
        "confidence": 0.92,
        "distancia_aprox_m": 1.5,
        "bbox": [0.12, 0.15, 0.45, 0.92]
      }
    ],
    "inference_ms": 142.5
  }
  ```

| Campo de Detección | Descripción |
| :--- | :--- |
| `label` | Etiqueta del objeto traducida al español. |
| `confidence` | Confianza de la predicción del modelo (rango 0 a 1). |
| `distancia_aprox_m` | Distancia aproximada al objeto, calculada en metros. |
| `bbox` | Bounding box normalizado `[x1, y1, x2, y2]` (valores entre 0.0 y 1.0) para dibujar sobre cualquier resolución de pantalla. |
| `inference_ms` | Tiempo que tomó la inferencia de la red en milisegundos. |

---

## Qué detecta el modelo

Utilizamos **YOLOv8n** (el modelo "nano" de Ultralytics, optimizado para velocidad en CPU) entrenado en el dataset de 80 clases **COCO**. Filtramos los resultados mediante un diccionario en [app/config.py](file:///c:/Users/demia/OneDrive/Desktop/disco/10mo%20semestre/Dispositivos%20moviles/Trabajos/OrientaGo/OrientaGo-Back/app/config.py) (`RELEVANT_CLASSES`) para enfocarnos solo en categorías de importancia peatonal:

* **Personas y Vehículos:** `persona`, `bicicleta`, `carro`, `motocicleta`, `bus`, `camión`, `tren`, `bote`
* **Señalización y Mobiliario:** `semáforo`, `hidrante`, `señal de alto`, `parquímetro`, `banco`, `maceta`
* **Animales domésticos y comunes:** `perro`, `gato`, `ave`, `caballo`, `oveja`, `vaca`
* **Objetos/Obstáculos en el suelo:** `mochila`, `paraguas`, `bolso`, `maleta`, `pelota`, `patineta`, `silla`, `sofá`, `mesa`

---

## Cómo funciona la estimación de distancia

Dado que un celular ordinario no cuenta con sensores de profundidad (LiDAR) o cámaras estereoscópicas calibradas, estimamos la distancia por medios geométricos (cámara monocular):

```text
distancia_aprox ≈ altura_real_del_objeto / (altura_relativa_en_imagen * constante_de_calibración)
```

Para evitar asumir que todos los objetos miden lo mismo, mapeamos en `REFERENCE_HEIGHTS_M` la altura promedio real (en metros) de cada categoría (por ejemplo, persona: `1.65m`, carro: `1.5m`, bus: `3.0m`, perro: `0.5m`).

Esto proporciona una indicación útil de proximidad ("cerca", "intermedio", "lejos"), no una medición de precisión métrica.

---

## Configuración y Ajustes

Las variables de configuración e inferencia están centralizadas en [app/config.py](file:///c:/Users/demia/OneDrive/Desktop/disco/10mo%20semestre/Dispositivos%20moviles/Trabajos/OrientaGo/OrientaGo-Back/app/config.py). Puedes ajustar los parámetros para calibrar el comportamiento del modelo:

| Parámetro | Propósito | Valor por Defecto |
| :--- | :--- | :--- |
| `CONF_THRESHOLD` | Confianza mínima requerida para reportar un objeto. | `0.45` |
| `NMS_THRESHOLD` | Umbral para Non-Maximum Suppression (eliminar cajas superpuestas). | `0.45` |
| `INPUT_SIZE` | Resolución de reescalado para el modelo. | `640` (píxeles) |
| `RELEVANT_CLASSES` | Diccionario de clases COCO rastreadas y su traducción a español. | Ver `app/config.py` |
| `REFERENCE_HEIGHTS_M` | Altura promedio asumida para cada categoría en metros. | Ver `app/config.py` |

---

## Solución de Problemas

#### `ERROR: Could not find a version that satisfies the requirement onnxruntime==1.18.0`
Ocurre si tu versión de Python es muy reciente para la versión fija de la biblioteca. En el actual `requirements.txt`, usamos operadores `>=` en lugar de versiones exactas, permitiendo a `pip` buscar e instalar la versión más actual compatible con tu sistema operativo y arquitectura de Python.

#### El celular no puede conectarse al servidor (aunque estén en la misma WiFi)
Windows Firewall suele bloquear conexiones entrantes en puertos no estándar. Puedes abrir el puerto 8000 ejecutando PowerShell como administrador y corriendo el siguiente comando:
```powershell
netsh advfirewall firewall add rule name="FastAPI 8000 Allow" dir=in action=allow protocol=TCP localport=8000
```
Prueba abriendo `http://IP_DE_TU_LAPTOP:8000/health` desde el navegador de tu celular para verificar la conexión de red.

#### `TypeError: Network request failed` desde la app móvil (pero carga en el navegador móvil)
No se trata de un problema del backend, sino de una restricción de React Native en cómo maneja los encabezados y estructuras en peticiones `multipart/form-data`. Revisa las instrucciones en el README de tu frontend.

#### El servidor no carga el modelo (`modelo_cargado: false` o error de archivo no encontrado)
Verifica que el archivo `yolov8n.onnx` esté correctamente ubicado en el directorio `models/` y no en otra ruta.

#### Las detecciones tardan mucho / baja tasa de FPS
El procesamiento en CPU es secuencial. Si tu máquina de desarrollo cuenta con recursos de hardware limitados, aumenta la variable `FRAME_INTERVAL_MS` en la pantalla de detección del frontend (`AnalizarEntornoScreen.tsx` o similar) para enviar fotogramas de forma más espaciada en lugar de tratar de forzar inferencia a tiempo real.

---

## Limitaciones Conocidas

* **Falta de detección de bordes y desniveles:** El modelo YOLO detecta objetos discretos definidos en su dataset, pero no detecta escaleras (subidas/bajadas), baches, irregularidades del terreno o fin de banquetas. El soporte de escaleras está propuesto como trabajo de fine-tuning futuro.
* **Cámara Monocular:** La distancia es una aproximación paramétrica. El ángulo del teléfono y el zoom digital de la cámara pueden alterar los resultados de distancia.
* **Procesamiento en Local:** La configuración actual con laptop y red local compartida es ideal para desarrollo y pruebas de MVP académico. En un escenario productivo se requiere desplegar el backend en la nube o migrar la inferencia directamente al chip del móvil.

---

## Roadmap / Próximos Pasos

* **Conversión a TFLite / CoreML:** Exportar el modelo YOLO a formatos comprimidos (`.tflite` para Android y `.mlmodel` para iOS) para correr inferencia 100% nativa en el procesador del móvil (elimina la dependencia del servidor y el WiFi).
* **Modelo especializado de desniveles:** Entrenar una red YOLO específica (o una red de segmentación) usando datasets locales para detectar gradas, desniveles de acera y alcantarillas abiertas.
* **Despliegue Cloud:** Subir el backend a servicios como Railway, Render o AWS para acceso global desde redes móviles (LTE/5G).
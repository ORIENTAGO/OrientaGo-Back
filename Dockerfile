FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc en disco y activar flushing del output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar requerimientos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código del backend
COPY . .

# Exponer el puerto del backend
EXPOSE 8000

# Comando para iniciar FastAPI
CMD python -m uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}


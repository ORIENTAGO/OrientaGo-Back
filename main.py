"""
Servidor MVP - Asistente Visual (Entrada principal reestructurada)
-----------------------------------------------------------------
Este archivo redirige la ejecución al módulo 'app.main:app' para conservar
la compatibilidad con el comando existente de uvicorn:
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
"""

from app.main import app

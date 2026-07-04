from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router

app = FastAPI(title="Asistente Visual - Servidor de Detección (MVP)")

# CORS abierto para pruebas en red local (WiFi del equipo)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

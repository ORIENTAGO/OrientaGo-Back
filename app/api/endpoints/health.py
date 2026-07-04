from fastapi import APIRouter
from app.config import MODEL_PATH
import os

router = APIRouter()

@router.get("/health")
def health():
    return {"status": "ok", "modelo_cargado": os.path.exists(MODEL_PATH)}

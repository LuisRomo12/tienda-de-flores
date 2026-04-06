from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import sys

# Agregamos la raíz a la ruta para poder importar de main si es necesario
sys.path.append('.')

from core.database import get_db
from repositories.flor_repository import FlorRepository

# Controladores (MVC Pattern)
router = APIRouter(prefix="/api/micro-catalog", tags=["CatalogService"])

@router.get("/flores")
async def get_public_flores_microservice(db: Session = Depends(get_db)):
    """
    Controlador MVC Puro. Usa el Repositorio de la capa inferior
    para obtener las flores sin tocar directamente consultas SQL en el endpoint.
    """
    repo = FlorRepository(db)
    flores = repo.get_todas_publicas()
    return flores

@router.get("/flores/{flor_id}")
async def get_public_flor_microservice(flor_id: int, db: Session = Depends(get_db)):
    repo = FlorRepository(db)
    flor = repo.get_por_id_publica(flor_id)
    if not flor:
        raise HTTPException(status_code=404, detail="Flor no encontrada en el catálogo.")
    return flor

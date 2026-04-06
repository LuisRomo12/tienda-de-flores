from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/micro-auth", tags=["AuthService"])

@router.get("/ping")
async def ping_auth_service():
    """
    Microservicio de Auth Independiente.
    Manejará el SSO y MFA.
    """
    return {"message": "Módulo de Seguridad operando independiente"}

from fastapi import APIRouter
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/micro-cart", tags=["CartService"])

@router.get("/ping")
async def ping_cart_service():
    """
    Microservicio de Carrito Independiente (Mock initial ping)
    Aquí residiría toda la lógica /user/carrito
    """
    return {"message": "El microservicio del carrito está corriendo de forma aislada"}

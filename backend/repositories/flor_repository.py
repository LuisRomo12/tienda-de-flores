from sqlalchemy import text
from repositories.base import BaseRepository

class FlorRepository(BaseRepository):
    """
    Repository Pattern: Mueve todo el código SQL y SQLAlchemy para la
    entidad 'Flor' a una capa separada del endpoint (Controlador).
    """

    def get_todas_publicas(self):
        result = self.db.execute(text("SELECT * FROM flores ORDER BY id DESC"))
        keys = result.keys()
        return [dict(zip(keys, row)) for row in result]

    def get_por_id_publica(self, flor_id: int):
        result = self.db.execute(text("SELECT * FROM flores WHERE id = :flor_id"), {"flor_id": flor_id})
        row = result.fetchone()
        if not row:
            return None
        return dict(zip(result.keys(), row))

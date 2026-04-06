from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

class DBConnectionFactory:
    """
    Factory / Singleton Pattern mixto para la gestión de base de datos.
    Crea el engine de manera perezosa y genera las sesiones.
    """
    _engine = None
    _session_local = None

    @classmethod
    def get_engine(cls):
        if cls._engine is None:
            # Aquí aplicamos el Factory Method (retorna una instancia de Engine basada en config)
            cls._engine = create_engine(settings.database_url)
        return cls._engine

    @classmethod
    def get_session_factory(cls):
        if cls._session_local is None:
            cls._session_local = sessionmaker(autocommit=False, autoflush=False, bind=cls.get_engine())
        return cls._session_local

Base = declarative_base()

def get_db():
    """Dependency injection para FastAPI"""
    db = DBConnectionFactory.get_session_factory()()
    try:
        yield db
    finally:
        db.close()

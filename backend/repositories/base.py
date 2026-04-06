class BaseRepository:
    """
    Clase base para el Repositorio de la aplicación.
    Establece la conexión de sesión a utilizar.
    """
    def __init__(self, db_session):
        self.db = db_session

import os
from dotenv import load_dotenv
import urllib.parse

class SettingsManager:
    """
    Singleton Pattern: Garantiza que la configuración y variables de entorno
    se carguen en memoria una sola vez.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SettingsManager, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        load_dotenv()
        self.secret_key = os.environ.get("SECRET_KEY", "b3c7d6e4f1a23998b47596c8a7413695")
        self.encryption_key = os.environ.get("ENCRYPTION_KEY", b"eYfQwU9f_GjA-qEa18v-tI10k7gT8N6P7l-_9E0D6oQ=")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 15
        self.refresh_token_expire_days = 7
        
        # Base de datos
        db_url_env = os.environ.get("DATABASE_URL")
        
        if db_url_env:
            if db_url_env.startswith("postgres://"):
                db_url_env = db_url_env.replace("postgres://", "postgresql://", 1)
            self.database_url = db_url_env
        else:
            self.db_user = os.environ.get("DB_USER", "postgres")
            self.db_password = os.environ.get("DB_PASSWORD", "password_secreta")
            try:
                password_encoded = urllib.parse.quote_plus(self.db_password)
                self.database_url = f"postgresql://{self.db_user}:{password_encoded}@localhost:5432/floreria_db"
            except Exception:
                self.database_url = "sqlite:///./fallback.db"

# Instancia global exportada
settings = SettingsManager()

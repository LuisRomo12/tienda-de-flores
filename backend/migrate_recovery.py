import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import urllib.parse
from sqlalchemy import create_engine, text

usuario = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "password_secreta")
password_encoded = urllib.parse.quote_plus(password)
DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)

def run_migration():
    with engine.connect() as conn:
        print("Comenzando migracion de Recuperacion...")
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN pregunta_secreta VARCHAR(255);"))
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN respuesta_secreta_hash VARCHAR(255);"))
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN recovery_attempts INTEGER DEFAULT 0;"))
        except Exception:
            pass
        try:
            conn.execute(text("ALTER TABLE users ADD COLUMN recovery_locked_until TIMESTAMP;"))
        except Exception:
            pass
        
        conn.commit()
        print("Migracion completada exitosamente.")

if __name__ == "__main__":
    run_migration()

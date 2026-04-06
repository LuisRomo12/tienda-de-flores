import os
from sqlalchemy import create_engine, text
import urllib.parse

# Configuracion de DB
usuario = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "password_secreta")
password_encoded = urllib.parse.quote_plus(password)
DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("Migrando tabla users...")
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN tema VARCHAR DEFAULT 'claro'"))
        conn.execute(text("ALTER TABLE users ADD COLUMN idioma VARCHAR DEFAULT 'es'"))
        conn.commit()
        print("Columnas agregadas a users.")
    except Exception as e:
        print("Error en users:", e)
        conn.rollback()

    print("Migrando tabla admins...")
    try:
        conn.execute(text("ALTER TABLE admins ADD COLUMN tema VARCHAR DEFAULT 'claro'"))
        conn.execute(text("ALTER TABLE admins ADD COLUMN idioma VARCHAR DEFAULT 'es'"))
        conn.commit()
        print("Columnas agregadas a admins.")
    except Exception as e:
        print("Error en admins:", e)
        conn.rollback()

print("Migracion completada exitosamente.")

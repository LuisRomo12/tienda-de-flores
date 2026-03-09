import os
import urllib.parse
from sqlalchemy import create_engine, text

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

usuario = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "password_secreta")
password_encoded = urllib.parse.quote_plus(password)
DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        # Check if column already exists
        res = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='flores' AND column_name='imagenes_extra'"))
        if not res.fetchone():
            print("Agregando columna 'imagenes_extra' a la tabla 'flores'...")
            conn.execute(text("ALTER TABLE flores ADD COLUMN imagenes_extra JSONB DEFAULT '[]'::jsonb"))
            conn.commit()
            print("¡Columna agregada exitosamente!")
        else:
            print("La columna 'imagenes_extra' ya existe en 'flores'.")
    except Exception as e:
        print(f"Error al modificar la base de datos: {e}")

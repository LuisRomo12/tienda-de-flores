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
        print("Agregando nuevas columnas a la tabla 'flores'...")
        # Add columns one by one, ignoring errors if they already exist
        queries = [
            "ALTER TABLE flores ADD COLUMN descripcion_detallada TEXT;",
            "ALTER TABLE flores ADD COLUMN sku VARCHAR(50) UNIQUE;",
            "ALTER TABLE flores ADD COLUMN tags VARCHAR(200);",
            "ALTER TABLE flores ADD COLUMN recomendaciones TEXT;"
        ]
        
        for q in queries:
            try:
                conn.execute(text(q))
                print(f"Query ejecutada: {q}")
            except Exception as e:
                print(f"Aviso (Posiblemente ya existe): {e}")
                
        conn.commit()
        print("Migración de metadatos finalizada.")
    except Exception as e:
        print(f"Error fatal al modificar la base de datos: {e}")

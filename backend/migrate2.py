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

with engine.connect() as conn:
    print("Migrating...")
    try:
        conn.execute(text("ALTER TABLE users ADD COLUMN tema VARCHAR DEFAULT 'claro'"))
        conn.execute(text("ALTER TABLE users ADD COLUMN idioma VARCHAR DEFAULT 'es'"))
        conn.commit()
    except Exception as e:
        print("users err:", e)
        conn.rollback()

    try:
        conn.execute(text("ALTER TABLE admins ADD COLUMN tema VARCHAR DEFAULT 'claro'"))
        conn.execute(text("ALTER TABLE admins ADD COLUMN idioma VARCHAR DEFAULT 'es'"))
        conn.commit()
    except Exception as e:
        print("admins err:", e)
        conn.rollback()
    
    print("Done")

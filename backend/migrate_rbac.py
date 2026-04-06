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
    print("Migrating RBAC...")
    try:
        conn.execute(text("ALTER TABLE admins ADD COLUMN rol VARCHAR DEFAULT 'editor'"))
        # Force the very first admin (usually id 1) to be 'admin' so they have full access
        conn.execute(text("UPDATE admins SET rol = 'admin' WHERE id = 1"))
        conn.commit()
    except Exception as e:
        print("admins RBAC err:", e)
        conn.rollback()
    
    print("Done")

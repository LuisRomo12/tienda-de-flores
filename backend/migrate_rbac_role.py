"""
Migración RBAC — Agrega columna 'role' a la tabla 'users'.

Ejecución:
    cd backend
    python migrate_rbac_role.py
"""
import os
import urllib.parse
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from sqlalchemy import create_engine, text

# ── Conexión ──────────────────────────────────────────────────────────────────
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    usuario  = os.environ.get("DB_USER", "postgres")
    password = urllib.parse.quote_plus(os.environ.get("DB_PASSWORD", "password_secreta"))
    db_url   = f"postgresql://{usuario}:{password}@localhost:5432/floreria_db"

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

engine = create_engine(db_url)

MIGRACIONES = [
    # 1. Agregar columna role a users (si no existe)
    """
    ALTER TABLE users
    ADD COLUMN IF NOT EXISTS role VARCHAR(20) NOT NULL DEFAULT 'user';
    """,

    # 2. Constraint CHECK para valores válidos
    """
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM pg_constraint WHERE conname = 'users_role_check'
        ) THEN
            ALTER TABLE users
            ADD CONSTRAINT users_role_check
            CHECK (role IN ('user', 'editor', 'admin', 'superadmin'));
        END IF;
    END
    $$;
    """,

    # 3. Índice para búsquedas frecuentes por rol
    """
    CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
    """,

    # 4. Asegurarse de que todos los usuarios existentes tengan el rol 'user'
    """
    UPDATE users SET role = 'user' WHERE role IS NULL OR role = '';
    """,
]

def run():
    with engine.connect() as conn:
        for i, sql in enumerate(MIGRACIONES, start=1):
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"[{i}/{len(MIGRACIONES)}] ✅ OK")
            except Exception as e:
                conn.rollback()
                print(f"[{i}/{len(MIGRACIONES)}] ⚠️  {e}")

    print("\n✅ Migración RBAC completada.")
    print("   Para asignar superadmin ejecuta en psql:")
    print("   UPDATE users SET role='superadmin' WHERE email='tu@email.com';")

if __name__ == "__main__":
    run()

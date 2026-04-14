"""
=============================================================================
MIGRACIÓN — Corrección columna 'precio' en tabla 'accesorios'
=============================================================================
Soluciona: psycopg2.errors.UndefinedColumn — column a.precio does not exist

Contexto del problema:
  La tabla 'accesorios' fue creada en una versión antigua del código sin la
  columna 'precio'. El CREATE TABLE IF NOT EXISTS en force_migration no la
  añade si la tabla ya existe. El ALTER TABLE posterior debería haberla
  agregado, pero pudo haber fallado silenciosamente si la columna fue
  declarada NOT NULL sin DEFAULT en una tabla con filas existentes.

Esta migración:
  1. Agrega 'precio' con DEFAULT 0 si no existe
  2. Agrega 'descripcion' y 'sku' si no existen
  3. Garantiza que filas anteriores tengan un valor válido en 'precio'
  4. Agrega un índice en 'precio' para JOINs del carrito

Ejecución:
    cd backend
    python migrate_accesorios_precio.py

NOTA: El proyecto no usa Alembic (no está en requirements.txt).
      Ver al final del archivo los comandos equivalentes de Alembic
      si decides migrarlo en el futuro.
=============================================================================
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

# ── Migraciones idempotentes (seguras para re-ejecutar) ───────────────────────
PASOS = [

    # PASO 1 ─ Agregar 'precio' si no existe
    # ADD COLUMN IF NOT EXISTS es PostgreSQL 9.6+
    # DEFAULT 0 es necesario para no romper filas existentes cuando la columna es NOT NULL
    (
        "Agregar columna precio a accesorios",
        """
        ALTER TABLE accesorios
        ADD COLUMN IF NOT EXISTS precio NUMERIC(10, 2) NOT NULL DEFAULT 0;
        """
    ),

    # PASO 2 ─ Agregar 'descripcion' si no existe
    (
        "Agregar columna descripcion a accesorios",
        """
        ALTER TABLE accesorios
        ADD COLUMN IF NOT EXISTS descripcion TEXT;
        """
    ),

    # PASO 3 ─ Agregar 'sku' si no existe
    (
        "Agregar columna sku a accesorios",
        """
        ALTER TABLE accesorios
        ADD COLUMN IF NOT EXISTS sku VARCHAR(50);
        """
    ),

    # PASO 4 ─ Actualizar filas que quedaron con precio=0 (migración de datos)
    # COALESCE garantiza que no queden NULLs si la columna se agregó con DEFAULT
    (
        "Corregir filas con precio nulo o cero heredadas",
        """
        UPDATE accesorios
        SET precio = 0
        WHERE precio IS NULL;
        """
    ),

    # PASO 5 ─ Índice en precio para optimizar JOINs del carrito
    (
        "Crear índice en accesorios.precio",
        """
        CREATE INDEX IF NOT EXISTS idx_accesorios_precio ON accesorios(precio);
        """
    ),

    # PASO 6 ─ Verificar que el carrito JOIN funciona correctamente
    (
        "Verificar JOIN carrito con accesorios (smoke test)",
        """
        SELECT a.id, a.nombre, a.precio
        FROM accesorios a
        LIMIT 1;
        """
    ),
]


def run():
    print("=" * 60)
    print("MIGRACION: columna precio en tabla accesorios")
    print("=" * 60)

    with engine.connect() as conn:
        for i, (descripcion, sql) in enumerate(PASOS, start=1):
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"  [{i}/{len(PASOS)}] OK   {descripcion}")
            except Exception as e:
                conn.rollback()
                print(f"  [{i}/{len(PASOS)}] WARN {descripcion}")
                print(f"         Error: {e}")

    print()
    print("Migracion completada.")
    print()
    print("Para verificar en psql:")
    print(r"  \d accesorios")
    print("  SELECT id, nombre, precio FROM accesorios LIMIT 5;")


if __name__ == "__main__":
    run()


# =============================================================================
# COMANDOS ALEMBIC EQUIVALENTES (si quisieras migrar el proyecto a Alembic)
# =============================================================================
#
# 1. Instalar Alembic:
#    pip install alembic
#    Agregar al requirements.txt: alembic==1.13.1
#
# 2. Inicializar en el backend/:
#    cd backend
#    alembic init alembic
#
# 3. Editar alembic/env.py — conectar tu DATABASE_URL:
#    from main import Base, DATABASE_URL
#    config.set_main_option("sqlalchemy.url", DATABASE_URL)
#    target_metadata = Base.metadata
#
# 4. Generar migración automática desde los modelos ORM:
#    alembic revision --autogenerate -m "add_precio_to_accesorios"
#    # Esto detecta FlorDB y AccesorioDB (recién agregados) y genera el script
#
# 5. Revisar el archivo generado en alembic/versions/xxxx_add_precio_to_accesorios.py
#    El upgrade() debería contener algo como:
#
#    def upgrade():
#        op.add_column('accesorios',
#            sa.Column('precio', sa.Numeric(10, 2), nullable=False, server_default='0'))
#        op.add_column('accesorios',
#            sa.Column('descripcion', sa.Text(), nullable=True))
#        op.add_column('accesorios',
#            sa.Column('sku', sa.String(50), nullable=True))
#
#    def downgrade():
#        op.drop_column('accesorios', 'precio')
#        op.drop_column('accesorios', 'descripcion')
#        op.drop_column('accesorios', 'sku')
#
# 6. Aplicar la migración:
#    alembic upgrade head
#
# 7. Ver historial de migraciones:
#    alembic history --verbose
#
# 8. Revertir la última migración:
#    alembic downgrade -1
# =============================================================================

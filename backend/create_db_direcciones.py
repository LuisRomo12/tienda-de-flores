import os
import urllib.parse
from sqlalchemy import create_engine, text

def create_direcciones_table():
    usuario = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "password_secreta")
    password_encoded = urllib.parse.quote_plus(password)
    DATABASE_URL = "postgresql://" + usuario + ":" + password_encoded + "@localhost:5432/floreria_db"

    engine = create_engine(DATABASE_URL)

    sql_commands = """
    CREATE TABLE IF NOT EXISTS direcciones (
        id                  SERIAL       PRIMARY KEY,
        user_id             INT          NOT NULL REFERENCES users(id) ON DELETE CASCADE,

        calle               VARCHAR(200) NOT NULL,
        sin_numero          BOOLEAN      DEFAULT FALSE,
        codigo_postal       VARCHAR(10),
        estado              VARCHAR(100),
        municipio           VARCHAR(100),
        localidad           VARCHAR(100),
        colonia             VARCHAR(100),
        num_interior        VARCHAR(20),
        indicaciones        VARCHAR(128),

        tipo_domicilio      VARCHAR(20)  DEFAULT 'residencial' CHECK (tipo_domicilio IN ('residencial', 'laboral')),
        nombre_contacto     VARCHAR(150),
        telefono_contacto   VARCHAR(20),

        es_principal        BOOLEAN      DEFAULT FALSE,
        created_at          TIMESTAMPTZ  DEFAULT NOW()
    );

    CREATE INDEX IF NOT EXISTS idx_direcciones_user ON direcciones(user_id);

    DROP INDEX IF EXISTS idx_direccion_principal;
    CREATE UNIQUE INDEX idx_direccion_principal 
        ON direcciones(user_id) 
        WHERE es_principal = TRUE;

    CREATE OR REPLACE FUNCTION check_max_direcciones()
    RETURNS TRIGGER AS $$
    BEGIN
        IF (SELECT COUNT(*) FROM direcciones WHERE user_id = NEW.user_id) >= 4 THEN
            RAISE EXCEPTION 'El usuario ya tiene un maximo de 4 direcciones permitidas';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;

    DROP TRIGGER IF EXISTS trg_max_direcciones ON direcciones;
    CREATE TRIGGER trg_max_direcciones
        BEFORE INSERT ON direcciones
        FOR EACH ROW EXECUTE FUNCTION check_max_direcciones();
    """

    try:
        with engine.begin() as conn:
            conn.execute(text(sql_commands))
            print("Table 'direcciones', indexes, and triggers created successfully.")
    except Exception as e:
        print(f"Error executing SQL: {e}")

if __name__ == "__main__":
    create_direcciones_table()

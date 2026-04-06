import os
import urllib.parse
from sqlalchemy import text, create_engine
from dotenv import load_dotenv

load_dotenv()

usuario = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "password_secreta")
password_encoded = urllib.parse.quote_plus(password)
DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        # Check if column exists to avoid errors on rerun
        def add_column_if_not_exists(table, column, definition):
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {definition}"))
                print(f"Added {column} to {table}")
            except Exception as e:
                print(f"Column {column} might already exist in {table} or error: {e}")
                
        # Commit manually if using non-autocommit
        with conn.begin():
            add_column_if_not_exists("users", "mfa_enabled", "BOOLEAN DEFAULT FALSE")
            add_column_if_not_exists("users", "mfa_secret", "VARCHAR(255) DEFAULT NULL")
            add_column_if_not_exists("admins", "mfa_enabled", "BOOLEAN DEFAULT FALSE")
            add_column_if_not_exists("admins", "mfa_secret", "VARCHAR(255) DEFAULT NULL")
            # The other tables will be created automatically by SQLAlchemy create_all()
            
if __name__ == "__main__":
    migrate()

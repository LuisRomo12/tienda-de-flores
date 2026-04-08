import os
import urllib.parse
from sqlalchemy import create_engine, inspect

usuario = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "password_secreta")
password_encoded = urllib.parse.quote_plus(password)
DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)

inspector = inspect(engine)
tables = inspector.get_table_names()

output = {}

for table_name in tables:
    columns = inspector.get_columns(table_name)
    col_info = []
    for c in columns:
        col_info.append(f"{c['name']} {c['type']}")
    output[table_name] = col_info

print("=== TABLES ===")
for t, cols in output.items():
    print(f"TABLE {t}:")
    for c in cols:
        print(f"  {c}")

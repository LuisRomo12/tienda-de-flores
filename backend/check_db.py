from sqlalchemy import create_engine, text
import urllib.parse

password_encoded = urllib.parse.quote_plus('password_secreta')
engine = create_engine(f'postgresql://postgres:{password_encoded}@localhost:5432/floreria_db')

try:
    with engine.connect() as conn:
        res1 = conn.execute(text('SELECT count(*) FROM pedidos')).scalar()
        res2 = conn.execute(text('SELECT count(*) FROM vista_pedidos')).scalar()
        res3 = conn.execute(text('SELECT count(*) FROM resumen_ventas_diario')).scalar()
        print(f"Pedidos: {res1}")
        print(f"Vista Pedidos: {res2}")
        print(f"Resumen Ventas: {res3}")
except Exception as e:
    print(f"Error: {e}")

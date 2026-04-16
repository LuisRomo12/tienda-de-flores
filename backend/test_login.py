import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ajusta las importaciones según la estructura real de tus archivos
from main import app, get_db, Base
from main import UserDB, get_password_hash  

from sqlalchemy.pool import StaticPool

# 1. Configurar una base de datos SQLite en memoria para mockear la BD
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. Sobrescribir la inyección de dependencias de la base de datos en FastAPI
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Instanciar el cliente de pruebas
client = TestClient(app)

# 3. Fixture para preparar la BD antes de las pruebas y limpiarla después
@pytest.fixture(scope="module", autouse=True)
def setup_database():
    # Crear la estructura de tablas usando SQLAlchemy (sin migraciones manuales)
    Base.metadata.create_all(bind=engine)
    
    # Insertar un usuario de prueba en la base de datos mockeada
    db = TestingSessionLocal()
    hashed_password = get_password_hash("qa_password_123") 
    test_user = UserDB(
        email="qa_test@correo.com",
        password=hashed_password
    )
    db.add(test_user)
    db.commit()
    db.close()
    
    yield # Aquí se ejecutan las pruebas
    
    # Desmontar tablas y limpiar memoria
    Base.metadata.drop_all(bind=engine)

# 4. Caso de Prueba 1: Login exitoso y validación de generación de JWT
def test_login_success():
    response = client.post(
        "/api/login", 
        json={"email": "qa_test@correo.com", "password": "qa_password_123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

# 5. Caso de Prueba 2: Rechazar credenciales incorrectas
def test_login_invalid_credentials():
    response = client.post(
        "/api/login",
        json={"email": "qa_test@correo.com", "password": "wrong_password"}
    )
    
    assert response.status_code in [400, 401]
    assert "detail" in response.json()

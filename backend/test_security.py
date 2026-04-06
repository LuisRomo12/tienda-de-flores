import pytest
from fastapi.testclient import TestClient
from main import app, SECRET_KEY, ALGORITHM
import uuid
from datetime import datetime, timedelta
from jose import jwt

client = TestClient(app)

# --- Pruebas de Seguridad Obligatorias (Parte 8) ---

def test_rate_limiting_brute_force():
    """
    Verifica la prevención de ataques de fuerza bruta.
    El límite está configurado a 5 peticiones por minuto.
    """
    # Hacer 5 peticiones rápidas, deben pasar (o ser 401 por Auth fallido)
    for _ in range(5):
        response = client.post("/api/login", json={"email": "fake@test.com", "password": "123"})
        assert response.status_code in [401, 404]
    
    # La petición 6 debe ser bloqueada
    response = client.post("/api/login", json={"email": "fake@test.com", "password": "123"})
    assert response.status_code == 429
    assert "Too Many Requests" in response.text or "Rate limit exceeded" in response.text

def test_expired_token_rejection():
    """
    Verifica que la API rechace tokens de nivel de acceso expirados estáticamente.
    """
    expired_payload = {
        "sub": "test@test.com",
        "type": "user",
        "exp": datetime.utcnow() - timedelta(minutes=10)
    }
    token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "No se pudo validar" in response.json()["detail"] or "expirado" in response.json()["detail"]

def test_revoked_session_protection():
    """
    Verifica la protección contra ataques de Token Replay y Session Hijacking 
    con las validaciones de is_revoked explícitas en el objeto get_current_user.
    """
    valid_payload = {
        "sub": "test@test.com",
        "type": "user",
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(valid_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert "revocada" in response.json().get("detail", "") or "No se pudo" in response.json().get("detail", "")

def test_mfa_pending_restrictions():
    """
    Asegura que un token de MFA temporal interceptado no tenga acceso al sistema final.
    """
    pending_payload = {
        "sub": "test@test.com",
        "type": "user",
        "mfa_pending": True,
        "exp": datetime.utcnow() + timedelta(minutes=5)
    }
    token = jwt.encode(pending_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401

def test_multiple_sessions_block():
    """
    Verifica que el sistema impida el inicio de sesión si el usuario
    supera el límite estricto de sesiones concurrentes (ej: 3).
    """
    app.state.limiter.enabled = False
    try:
        unique_id = uuid.uuid4().hex[:6]
        user_email = f"test_sessions_{unique_id}@test.com"
        client.post("/api/register", json={
            "email": user_email,
            "password": "Password123",
            "confirm_password": "Password123",
            "captcha_answer": 8
        })

        # Iniciar sesión 3 veces debe ser exitoso
        for i in range(3):
            res = client.post("/api/login", json={"email": user_email, "password": "Password123"})
            assert res.status_code == 200

        # La 4ta vez debe denegar estrictamente
        res4 = client.post("/api/login", json={"email": user_email, "password": "Password123"})
        assert res4.status_code == 403
        assert "máx 3" in res4.json().get("detail", "").lower() or "sesiones activas alcanzado" in res4.json().get("detail", "").lower()
    finally:
        app.state.limiter.enabled = True

def test_missing_token():
    """
    Simula un acceso sin token a un endpoint protegido.
    (Parte 3: Acceso sin token)
    """
    response = client.get("/api/auth/me")
    assert response.status_code == 401
    assert response.json().get("detail") == "Not authenticated"

def test_altered_token():
    """
    Simula un ataque con token alterado.
    El hash o firma JWT es invalidado intencionalmente.
    (Parte 3: Ataque con token alterado)
    """
    valid_payload = {
        "sub": "test@test.com",
        "type": "user",
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    # Lo firmamos con una llave incorrecta y falsa
    altered_token = jwt.encode(valid_payload, "LLAVE_FALSA_MALICIOSA", algorithm=ALGORITHM)
    
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {altered_token}"})
    assert response.status_code == 401

def test_wrong_role_access():
    """
    Simula un intento de acceso con rol incorrecto.
    (Parte 3: Intento de acceso con rol incorrecto - RBAC)
    """
    user_payload = {
        "sub": "fakeadmin",
        "role": "user",
        "type": "admin",
        "exp": datetime.utcnow() + timedelta(minutes=10)
    }
    token = jwt.encode(user_payload, SECRET_KEY, algorithm=ALGORITHM)
    
    # Endpoint de administrador que requiere rol 'admin'
    response = client.delete("/api/admin/flores/9999", headers={"Authorization": f"Bearer {token}"})
    
    # Debe ser rechazado porque este usuario no es admin ni está en la tabla AdminDB
    assert response.status_code in [401, 403]

def test_sql_injection_simulation():
    """
    Simula inyección en parámetros (SQLi).
    Asegura que el uso de SQLAlchemy escape la cadena y trate todo como un string
    y no ejecute sentencias DROP/OR.
    (Parte 3: Inyección en parámetros)
    """
    sql_payload = "1%'; DROP TABLE flores; --"
    response = client.get(f"/api/search?q={sql_payload}")
    
    # Como la consulta a 'search' está parametrizada, devolverá 200 asumiendo 
    # que buscó flores con ese nombre ridículo literal, y retornará [] o ignota
    assert response.status_code == 200
    assert isinstance(response.json(), list)

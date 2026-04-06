# Reporte Estricto de Seguridad - UTFLOWER

Este documento describe formalmente las mitigaciones exhaustivas implementadas contra las principales vulnerabilidades en el marco de la Parte 8 del sistema central.

## 1. Rate Limiting (Fuerza Bruta y Credential Stuffing)
Implementamos protección granular por IP usando la librería **SlowAPI**.
- Hemos decorado todos los endpoints de autenticación críticos (`/api/login`, `/api/admin/login`, y la totalidad del módulo en `/recovery/...`) con el límite estricto `@limiter.limit("5/minute")`.
- Si un atacante automatiza peticiones ilegítimas usando bots o scripts, el API lo mitigará cortando la conexión tras 5 fallos con HTTP `429 Too Many Requests`.
- Para el endpoint de "Preguntas Secretas", decidimos endurecer usando una política de estado basada en DB (`recovery_attempts`, `recovery_locked_until`), congelando permanentemente la cuenta por 15 minutos en el tercer fallo.

## 2. Prevención de Session Hijacking y Token Replay
Para la mitigación de secuestro de interacciones, seguimos un formato de doble llave (Access/Refresh Token):
- **Access Tokens de Corta Vida:** Generamos tokens expirables a los 15 minutos.
- **Refresh Tokens Blindados:** Manipulación del lado del servidor. Las cookies HttpOnly garantizan protección por defecto ante filtrado (XSS).
- **Session Replay Protection Activa:** La validación de interceptor en `get_current_user` ahora consulta a `SessionDB`. Si las sesiones del usuario fueron reportadas robadas y marcadas con `is_revoked = True`, hasta el Access Token legítimo temporalmente viviente será rebotado proactivamente negando privilegios (`401 Unauthorized`).

## 3. Prevención de Inyección de Código Estática (SQLi, XSS)
- **SQL Injection:** El backend nunca interpola sintaxis humana. Todas las uniones se resuelven a través de un modelizado seguro por Objetos (`SQLAlchemy`) con binding paramétrico por default.
- **Cross-Site Scripting (XSS):** Vue.js auto-drena y escapa todas las renderizaciones con doble-llave `{{}}` predeterminadamente.

## 4. Ejecución del Pentesting Interno Automatizado
Para probar estructuralmente la eficacia de mitigaciones (Brute Force, Replay Protection, Lifecycle), usa **PyTest**:

```bash
cd backend
pip install pytest httpx
pytest test_security.py -v --disable-warnings
```

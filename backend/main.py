from fastapi import FastAPI, HTTPException, status, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text, ForeignKey, DateTime, Table, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from passlib.context import CryptContext
from jose import jwt, JWTError
from cryptography.fernet import Fernet
from datetime import datetime, timedelta
import urllib.parse
import os
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
import io
import base64
from PIL import Image
from decimal import Decimal

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURACIÓN DE SEGURIDAD JWT ---
SECRET_KEY = os.environ.get("SECRET_KEY", "b3c7d6e4f1a23998b47596c8a7413695") # Cambiar en producción (.env)
ALGORITHM = "HS256"
ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY", b"eYfQwU9f_GjA-qEa18v-tI10k7gT8N6P7l-_9E0D6oQ=")
cipher_suite = Fernet(ENCRYPTION_KEY)
ACCESS_TOKEN_EXPIRE_MINUTES = 15 # Changed to 15 mins for better security
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_refresh_token(account_id: int, account_type: str):
    jti = str(uuid.uuid4())
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": str(account_id), "type": account_type, "jti": jti, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, jti, expire

def verify_password(plain_password, hashed_password):
    # Bcrypt falla si el input tiene > 72 bytes
    return pwd_context.verify(plain_password[:72], hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password[:72])

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def compress_image_b64(base64_string: str, max_dimension: int = 800, quality: int = 85) -> str:
    """Takes a base64 string, compresses the image with Pillow, and returns a new base64 string."""
    if not base64_string or not base64_string.startswith("data:image"):
        return base64_string  # Return as-is if it's not a valid data URI or is None

    try:
        # Extraer el header (ej. "data:image/jpeg;base64,") y el contenido real
        header, encoded = base64_string.split(",", 1)
        
        # Omit decoding if it's already sufficiently small or we want to force compress
        image_data = base64.b64decode(encoded)
        image = Image.open(io.BytesIO(image_data))
        
        # Resize if dimensions exceed max_dimension
        if image.width > max_dimension or image.height > max_dimension:
            # maintain aspect ratio
            image.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
        # Convert to RGB if it has alpha channel (PNG) to save as JPEG
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
            
        # Save to buffer
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", optimize=True, quality=quality)
        
        # Build new base64 string
        new_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{new_base64}"
    except Exception as e:
        print(f"Error comprimiendo imagen: {e}")
        return base64_string  # If compression fails, return the original string safely

# --- CONFIGURACIÓN DE DB ---
db_url_env = os.environ.get("DATABASE_URL")
if db_url_env:
    if db_url_env.startswith("postgres://"):
        db_url_env = db_url_env.replace("postgres://", "postgresql://", 1)
    DATABASE_URL = db_url_env
else:
    usuario = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "password_secreta")
    password_encoded = urllib.parse.quote_plus(password)
    DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association tables para RBAC
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id', ondelete='CASCADE'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'), primary_key=True)
)

# Jerarquía de roles RBAC
# superadmin > admin > editor > user
ROLES_JERARQUIA = ["user", "editor", "admin", "superadmin"]

# Modelo de la Tabla (Esto creará la tabla 'users')
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    tema = Column(String, default='claro')
    idioma = Column(String, default='es')
    pregunta_secreta = Column(String(255), nullable=True)
    respuesta_secreta_hash = Column(String(255), nullable=True)
    recovery_attempts = Column(Integer, default=0)
    recovery_locked_until = Column(TIMESTAMP, nullable=True)
    # Campo RBAC: rol simple para acceso rápido sin JOIN
    # Valores: 'user' | 'editor' | 'admin' | 'superadmin'
    role = Column(String(20), default='user', nullable=False, server_default='user')
    roles = relationship("RoleDB", secondary=user_roles)

class AdminDB(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nombre = Column(String)
    activo = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)
    tema = Column(String, default='claro')
    idioma = Column(String, default='es')
    rol = Column(String, default='editor')

class DireccionDB(Base):
    __tablename__ = "direcciones"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    calle = Column(String(200), nullable=False)
    sin_numero = Column(Boolean, default=False)
    codigo_postal = Column(String(10))
    estado = Column(String(100))
    municipio = Column(String(100))
    localidad = Column(String(100))
    colonia = Column(String(100))
    num_interior = Column(String(20))
    indicaciones = Column(String(128))
    tipo_domicilio = Column(String(20), default='residencial')
    nombre_contacto = Column(String(150))
    telefono_contacto = Column(String(20))
    es_principal = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Modelos ORM para tablas gestionadas por SQL manual
# extend_existing=True evita conflicto con create_all si la tabla ya existe
class FlorDB(Base):
    __tablename__ = "flores"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    precio = Column(String)  # NUMERIC en DB
    stock = Column(Integer, default=0)
    imagen_url = Column(Text, nullable=True)
    imagenes_extra = Column(Text, nullable=True)
    descripcion_detallada = Column(Text, nullable=True)
    sku = Column(String(50), nullable=True)
    tags = Column(String(200), nullable=True)
    recomendaciones = Column(Text, nullable=True)

class AccesorioDB(Base):
    __tablename__ = "accesorios"
    __table_args__ = {"extend_existing": True}
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    categoria_id = Column(Integer, ForeignKey("accesorios_categorias.id"), nullable=True)
    precio = Column(String, nullable=True)  # NUMERIC en DB; nullable para compatibilidad con filas antiguas
    stock = Column(Integer, default=0)
    imagen_data = Column(Text, nullable=True)
    descripcion = Column(Text, nullable=True)
    sku = Column(String(50), nullable=True)

class RoleDB(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    permissions = relationship("PermissionDB", secondary=role_permissions)

class PermissionDB(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)

class SessionDB(Base):
    __tablename__ = 'sessions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(Integer, nullable=False)
    account_type = Column(String(10), nullable=False) # 'user' or 'admin'
    refresh_token_jti = Column(String(255), unique=True, nullable=False)
    user_agent = Column(Text)
    ip_address = Column(String(45))
    expires_at = Column(TIMESTAMP, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class PasswordRecoveryDB(Base):
    __tablename__ = 'password_recovery'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    account_id = Column(Integer, nullable=False)
    account_type = Column(String(10), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(TIMESTAMP, nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

# ── MIGRACIÓN TEMPORAL DE PRODUCCIÓN ─────────────────────────────────────────
# Agrega columnas faltantes en la tabla 'accesorios' (precio, descripcion, sku)
# Seguro de re-ejecutar: usa IF NOT EXISTS / idempotente
# TODO: Eliminar este bloque después de confirmar un deploy exitoso en Render
try:
    import sys, os
    _dir = os.path.dirname(os.path.abspath(__file__))
    _script = os.path.join(_dir, "migrate_accesorios_precio.py")
    if os.path.exists(_script):
        import subprocess
        result = subprocess.run(
            [sys.executable, _script],
            capture_output=True, text=True, timeout=30
        )
        print("[STARTUP MIGRATION] accesorios_precio:")
        print(result.stdout)
        if result.returncode != 0:
            print("[STARTUP MIGRATION] WARN:", result.stderr)
except Exception as _me:
    print(f"[STARTUP MIGRATION] Error (no critico): {_me}")
# ── FIN MIGRACIÓN TEMPORAL ────────────────────────────────────────────────────

# Crear tablas automáticamente al iniciar
Base.metadata.create_all(bind=engine)



limiter = Limiter(key_func=get_remote_address)

app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5501",
        "http://127.0.0.1:5501",
        "https://tienda-de-flores.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/api/admin/force-migration")
def force_migration(db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    if current_admin.rol != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores con rol 'admin' pueden ejecutar migraciones")
    mig_queries = [
        """
        CREATE TABLE IF NOT EXISTS categorias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS flores (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            categoria_id INTEGER REFERENCES categorias(id),
            precio NUMERIC(10, 2) NOT NULL,
            stock INTEGER DEFAULT 0,
            imagen_url TEXT,
            imagenes_extra TEXT,
            descripcion_detallada TEXT,
            sku VARCHAR(50),
            tags VARCHAR(200),
            recomendaciones TEXT
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS accesorios_categorias (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            icono VARCHAR(50)
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS accesorios (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(255) NOT NULL,
            categoria_id INTEGER REFERENCES accesorios_categorias(id),
            precio NUMERIC(10, 2) NOT NULL,
            stock INTEGER DEFAULT 0,
            imagen_data TEXT,
            descripcion TEXT,
            sku VARCHAR(50)
        );
        """,
        "ALTER TABLE flores ADD COLUMN descripcion_detallada TEXT;",
        "ALTER TABLE flores ADD COLUMN sku VARCHAR(50);",
        "ALTER TABLE flores ADD COLUMN tags VARCHAR(200);",
        "ALTER TABLE flores ADD COLUMN recomendaciones TEXT;",
        "ALTER TABLE flores ALTER COLUMN imagen_url TYPE TEXT;",
        "ALTER TABLE flores ALTER COLUMN imagenes_extra TYPE TEXT;",
        """
        CREATE TABLE IF NOT EXISTS carrito (
            id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS carrito_items (
            id SERIAL PRIMARY KEY,
            carrito_id INTEGER REFERENCES carrito(id) ON DELETE CASCADE,
            flor_id INTEGER REFERENCES flores(id) ON DELETE CASCADE NULL,
            accesorio_id INTEGER REFERENCES accesorios(id) ON DELETE CASCADE NULL,
            cantidad INTEGER NOT NULL DEFAULT 1,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS pedidos (
            id SERIAL PRIMARY KEY,
            fecha_pedido TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estado VARCHAR(50) DEFAULT 'pendiente',
            total NUMERIC(10, 2) DEFAULT 0,
            user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
        );
        """,
        """
        CREATE OR REPLACE VIEW vista_pedidos AS 
        SELECT p.*, u.email as usuario_email 
        FROM pedidos p 
        LEFT JOIN users u ON p.user_id = u.id;
        """,
        """
        CREATE OR REPLACE VIEW resumen_ventas_diario AS 
        SELECT DATE(fecha_pedido) as dia, count(*) as cantidad_pedidos, SUM(total) as ingresos 
        FROM pedidos 
        GROUP BY DATE(fecha_pedido);
        """,
        # Migración para asegurar columnas de accesorios en producción
        "ALTER TABLE accesorios ADD COLUMN IF NOT EXISTS precio NUMERIC(10, 2) NOT NULL DEFAULT 0;",
        "ALTER TABLE accesorios ADD COLUMN IF NOT EXISTS sku VARCHAR(50);",
        "ALTER TABLE accesorios ADD COLUMN IF NOT EXISTS descripcion TEXT;",
    ]
    results = {}
    for q in mig_queries:
        try:
            db.execute(text(q))
            db.commit()
            results[q] = "Exito"
        except Exception as e:
            db.rollback()
            results[q] = f"Error: {e}"
    return results

# --- MODELOS DE VALIDACIÓN (Pydantic) ---
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    captcha_answer: int

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v, info):
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('Las contraseñas no coinciden')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class AdminCreate(BaseModel):
    username: str
    password: str
    nombre: str

class AdminLogin(BaseModel):
    username: str
    password: str

from typing import Optional

class DireccionBase(BaseModel):
    calle: str
    sin_numero: Optional[bool] = False
    codigo_postal: Optional[str] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    localidad: Optional[str] = None
    colonia: Optional[str] = None
    num_interior: Optional[str] = None
    indicaciones: Optional[str] = None
    tipo_domicilio: Optional[str] = "residencial"
    nombre_contacto: Optional[str] = None
    telefono_contacto: Optional[str] = None
    es_principal: Optional[bool] = False

class DireccionCreate(DireccionBase):
    pass

class DireccionResponse(DireccionBase):
    id: int
    user_id: int
    created_at: datetime
    class Config:
        from_attributes = True

class CartItemCreate(BaseModel):
    flor_id: Optional[int] = None
    accesorio_id: Optional[int] = None
    cantidad: int = 1

    @field_validator('cantidad')
    @classmethod
    def check_cantidad(cls, v):
        if v < 1:
            raise ValueError('La cantidad debe ser al menos 1')
        return v

class CartItemUpdate(BaseModel):
    cantidad: int

# --- RUTAS DE AUTENTICACIÓN ---

# Dependencia para proteger rutas de admin
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/admin/login")

async def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role not in ["admin", "editor", "web_admin"]:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    admin = db.query(AdminDB).filter(AdminDB.username == username).first()
    if admin is None or not admin.activo:
        raise credentials_exception
    return admin

oauth2_user_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_current_user(token: str = Depends(oauth2_user_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales de usuario",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Fix 3: Rechazar tokens temporales MFA que no deben acceder a rutas protegidas
        if payload.get("mfa_pending"):
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user is None:
        raise credentials_exception
    
    # Session Replay Protection: Verificar que tenga al menos una sesión activa (no revocada)
    active_session = db.query(SessionDB).filter(
        SessionDB.account_id == user.id, 
        SessionDB.account_type == "user", 
        SessionDB.is_revoked == False
    ).first()
    
    if not active_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Su sesión ha sido revocada o cerrada remotamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    return user


def check_role(roles_permitidos: list[str]):
    """
    Factory de dependency RBAC para FastAPI.
    Recibe una lista de roles permitidos y retorna una dependency
    que valida que el usuario autenticado tenga uno de esos roles.

    Jerarquía: superadmin > admin > editor > user
    Ejemplo de uso:
        @app.delete("/recurso/{id}")
        async def eliminar(current_user = Depends(check_role(["admin", "superadmin"]))):
            ...
    """
    def dependency(current_user: UserDB = Depends(get_current_user)):
        if current_user.role not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Tu rol '{current_user.role}' no tiene permiso. "
                       f"Se requiere uno de: {roles_permitidos}"
            )
        return current_user
    return dependency


def check_min_role(min_role: str):
    """
    Alternativa jerárquica: permite acceso si el rol del usuario
    es igual o superior al rol mínimo requerido.
    Ejemplo: check_min_role('editor') permite a editor, admin y superadmin.
    """
    def dependency(current_user: UserDB = Depends(get_current_user)):
        user_level = ROLES_JERARQUIA.index(current_user.role) if current_user.role in ROLES_JERARQUIA else -1
        min_level = ROLES_JERARQUIA.index(min_role) if min_role in ROLES_JERARQUIA else 999
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acceso denegado. Se requiere al menos el rol '{min_role}'."
            )
        return current_user
    return dependency


@app.post("/api/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
async def register_user(request: Request, user: UserCreate, db: Session = Depends(get_db)):
    # 1. Validar Captcha
    if user.captcha_answer != 8:
        raise HTTPException(status_code=400, detail="CAPTCHA incorrecto")
    
    # 2. Verificar si el correo ya existe en la DB
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El correo ya está registrado")

    # 3. Guardar en Postgres seguro (hashear contraseña)
    hashed_pwd = get_password_hash(user.password)
    new_user = UserDB(email=user.email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    return {"message": "Usuario registrado exitosamente en PostgreSQL"}

@app.post("/api/admin/register", status_code=status.HTTP_201_CREATED)
async def register_admin(admin: AdminCreate, db: Session = Depends(get_db)):
    db_admin = db.query(AdminDB).filter(AdminDB.username == admin.username).first()
    if db_admin:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está registrado")

    hashed_pwd = get_password_hash(admin.password)
    new_admin = AdminDB(username=admin.username, password_hash=hashed_pwd, nombre=admin.nombre)
    db.add(new_admin)
    db.commit()
    return {"message": "Administrador registrado exitosamente"}

# --- SEGURIDAD: PREVENCIÓN DE VULNERABILIDADES ---
# 1. SQL Injection (SQLi): Se previene con el uso implícito de queries parametrizadas mediante SQLAlchemy (ej. DB.query o text(".. :val")).
# 2. XSS (Cross-Site Scripting): En el backend se asegura no sirviendo HTML, retornando puramente Content-Type application/json. Vue.js en el front-end auto-escapa HTML en interpolaciones automáticamente.
# 3. CSRF (Cross-Site Request Forgery): Prevenido combinando el uso de Bearer Tokens para state-changing actions y configurando cookies SameSite=lax.
# 4. Brute Force y Credential Stuffing: Prevenido configurando límites estrictos (@limiter.limit) en todos los endpoints de autenticación y recuperación.
# 5. Session Hijacking & Token Replay: Tokens de acceso tienen caducidad muy corta (15 min). La base de datos de sesiones registra los UUID (jti) de cada refresh token. Si se revoca la sesión activa (logout, o ataque), se bloquea para siempre chequeando `is_revoked`.

@app.post("/api/admin/login")
@limiter.limit("5/minute")
async def login_admin(request: Request, response: Response, admin: AdminLogin, db: Session = Depends(get_db)):
    db_admin = db.query(AdminDB).filter(AdminDB.username == admin.username).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El usuario o la contraseña son incorrectos")
    
    if not verify_password(admin.password, db_admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El usuario o la contraseña son incorrectos")
    
    if not db_admin.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Esta cuenta de administrador está inactiva")

    if db_admin.mfa_enabled:
        temp_token_expires = timedelta(minutes=5)
        temp_token = create_access_token(
            data={"sub": str(db_admin.id), "role": "web_admin", "type": "admin", "mfa_pending": True}, 
            expires_delta=temp_token_expires
        )
        return {"mfa_required": True, "temp_token": temp_token}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_admin.username, "role": db_admin.rol, "type": "admin"}, expires_delta=access_token_expires
    )
    refresh_token, jti, expires_at = create_refresh_token(db_admin.id, "admin")

    active_sessions = db.query(SessionDB).filter(
        SessionDB.account_id == db_admin.id,
        SessionDB.account_type == "admin",
        SessionDB.is_revoked == False
    ).order_by(SessionDB.created_at).all()
    if len(active_sessions) >= 3:
        # Auto-cerrar las sesiones más antiguas, dejando solo 2 activas antes de registrar la nueva
        for s in active_sessions[:-2]:
            s.is_revoked = True
        db.commit()

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    db_session = SessionDB(account_id=db_admin.id, account_type="admin", refresh_token_jti=jti, expires_at=expires_at, user_agent=user_agent, ip_address=ip_address)
    db.add(db_session)
    db.commit()

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax", expires=expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    return {"access_token": access_token, "token_type": "bearer", "nombre": db_admin.nombre, "role": db_admin.rol}

@app.post("/api/login")
@limiter.limit("5/minute")
async def login_user(request: Request, response: Response, user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El correo o la contraseña son incorrectos")
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El correo o la contraseña son incorrectos")
    
    if db_user.mfa_enabled:
        temp_token_expires = timedelta(minutes=5)
        temp_token = create_access_token(
            data={"sub": str(db_user.id), "type": "user", "mfa_pending": True}, 
            expires_delta=temp_token_expires
        )
        return {"mfa_required": True, "temp_token": temp_token}

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        # Incluir 'role' en el JWT para que el frontend pueda leerlo sin extra requests
        data={"sub": db_user.email, "type": "user", "role": db_user.role},
        expires_delta=access_token_expires
    )
    refresh_token, jti, expires_at = create_refresh_token(db_user.id, "user")

    active_sessions = db.query(SessionDB).filter(
        SessionDB.account_id == db_user.id,
        SessionDB.account_type == "user",
        SessionDB.is_revoked == False
    ).order_by(SessionDB.created_at).all()
    if len(active_sessions) >= 3:
        # Auto-cerrar las sesiones más antiguas, dejando solo 2 activas antes de registrar la nueva
        for s in active_sessions[:-2]:
            s.is_revoked = True
        db.commit()

    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    db_session = SessionDB(account_id=db_user.id, account_type="user", refresh_token_jti=jti, expires_at=expires_at, user_agent=user_agent, ip_address=ip_address)
    db.add(db_session)
    db.commit()

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax", expires=expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/refresh")
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No se encontró token de actualización")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        account_id = int(payload.get("sub"))
        account_type = payload.get("type")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
        
    db_session = db.query(SessionDB).filter(SessionDB.refresh_token_jti == jti).first()
    if not db_session or db_session.is_revoked or db_session.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Sesión expirada o revocada")
        
    if account_type == "admin":
        admin = db.query(AdminDB).filter(AdminDB.id == account_id).first()
        access_token = create_access_token(data={"sub": admin.username, "role": "web_admin", "type": "admin"})
    else:
        user = db.query(UserDB).filter(UserDB.id == account_id).first()
        # Refresh también incluye el rol actualizado desde DB
        access_token = create_access_token(data={"sub": user.email, "type": "user", "role": user.role})
        
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/auth/logout")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    token = request.cookies.get("refresh_token")
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            jti = payload.get("jti")
            db_session = db.query(SessionDB).filter(SessionDB.refresh_token_jti == jti).first()
            if db_session:
                db_session.is_revoked = True
                db.commit()
        except:
            pass
    response.delete_cookie("refresh_token")
    return {"message": "Sesión cerrada"}

@app.get("/api/auth/me")
async def get_me(current_user: UserDB = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "mfa_enabled": current_user.mfa_enabled,
        "idioma": current_user.idioma,
        "tema": current_user.tema
    }

# ================================================================
#  NUEVAS RUTAS FRONTEND PÚBLICAS
# ================================================================

@app.get("/api/categorias")
async def get_public_categorias(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM categorias ORDER BY id"))
    keys = result.keys()
    categorias = [dict(zip(keys, row)) for row in result]
    return categorias

@app.get("/api/accesorios_categorias")
async def get_public_accesorios_categorias(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM accesorios_categorias ORDER BY id"))
    keys = result.keys()
    categorias = [dict(zip(keys, row)) for row in result]
    return categorias

@app.get("/api/accesorios")
async def get_public_accesorios(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM accesorios ORDER BY id DESC"))
    keys = result.keys()
    accesorios = [dict(zip(keys, row)) for row in result]
    return accesorios

@app.get("/api/accesorios/{accesorio_id}")
async def get_public_accesorio(accesorio_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM accesorios WHERE id = :accesorio_id"), {"accesorio_id": accesorio_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Accesorio no encontrado")
    keys = result.keys()
    return dict(zip(keys, row))

@app.get("/api/flores")
async def get_public_flores(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM flores ORDER BY id DESC"))
    keys = result.keys()
    flores = [dict(zip(keys, row)) for row in result]
    return flores

@app.get("/api/flores/{flor_id}")
async def get_public_flor(flor_id: int, db: Session = Depends(get_db)):
    result = db.execute(text("SELECT * FROM flores WHERE id = :flor_id"), {"flor_id": flor_id})
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Flor no encontrada")
    keys = result.keys()
    return dict(zip(keys, row))

@app.get("/api/search")
async def search_flores(
    q: str = "",
    category: str = "",
    max_price: float = 2000,
    only_stock: bool = False,
    db: Session = Depends(get_db)
):
    query = "SELECT * FROM flores WHERE precio <= :max_price"
    params = {"max_price": max_price}
    
    if q:
        query += " AND nombre ILIKE :q"
        params["q"] = f"%{q}%"
        
    if category:
        # Obtain category id from name
        cat_result = db.execute(text("SELECT id FROM categorias WHERE nombre = :category"), {"category": category})
        cat_row = cat_result.fetchone()
        if cat_row:
            query += " AND categoria_id = :category_id"
            params["category_id"] = cat_row[0]
            
    if only_stock:
        query += " AND stock > 0"
        
    query += " ORDER BY id DESC"
    
    result = db.execute(text(query), params)
    keys = result.keys()
    flores = [dict(zip(keys, row)) for row in result]
    
    # Format the category name backwards for the front-end to consume easily
    # Since Catalog.vue expects 'category' string
    for flor in flores:
        cat_res = db.execute(text("SELECT nombre FROM categorias WHERE id = :cid"), {"cid": flor["categoria_id"]})
        cr = cat_res.fetchone()
        flor["category"] = cr[0] if cr else "S/C"
        flor["name"] = flor["nombre"]
        flor["price"] = flor["precio"]
    
    return flores

# ================================================================
#  NUEVAS RUTAS ADMIN (Reemplazando PostgREST)
# ================================================================

@app.get("/api/admin/categorias")
async def get_categorias(db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    result = db.execute(text("SELECT id, nombre FROM categorias"))
    categorias = [{"id": row[0], "nombre": row[1]} for row in result]
    return categorias

@app.get("/api/admin/flores")
async def get_flores(db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    result = db.execute(text("SELECT * FROM flores ORDER BY id DESC"))
    # Convertir el resultado de SQLAlchemy a dict
    keys = result.keys()
    flores = [dict(zip(keys, row)) for row in result]
    return flores

import json

@app.post("/api/admin/flores")
async def create_flor(flor: dict, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    # Ejecuta un RAW insert
    
    # Compress Extra Images if present
    extra_images = flor.get("imagenes_extra", [])
    compressed_extra = []
    if isinstance(extra_images, list):
        for img in extra_images:
            compressed = compress_image_b64(img)
            compressed_extra.append(compressed)
            
    query = text("""
        INSERT INTO flores (nombre, categoria_id, precio, stock, imagen_url, imagenes_extra, descripcion_detallada, sku, tags, recomendaciones) 
        VALUES (:nombre, :categoria_id, :precio, :stock, :imagen_url, :imagenes_extra, :descripcion_detallada, :sku, :tags, :recomendaciones)
        RETURNING *
    """)
    result = db.execute(query, {
        "nombre": flor.get("nombre"),
        "categoria_id": flor.get("categoria_id"),
        "precio": flor.get("precio"),
        "stock": flor.get("stock", 0),
        "imagen_url": compress_image_b64(flor.get("imagen_url")),
        "imagenes_extra": json.dumps(compressed_extra),
        "descripcion_detallada": flor.get("descripcion_detallada"),
        "sku": flor.get("sku"),
        "tags": flor.get("tags"),
        "recomendaciones": flor.get("recomendaciones")
    })
    db.commit()
    keys = result.keys()
    nueva_flor = dict(zip(keys, result.fetchone()))
    return nueva_flor

# Whitelist de columnas permitidas para PATCH flores (previene SQL Injection en nombres de columna)
COLUMNAS_FLORES_PERMITIDAS = {
    "nombre", "categoria_id", "precio", "stock", "imagen_url",
    "imagenes_extra", "descripcion_detallada", "sku", "tags", "recomendaciones"
}

@app.patch("/api/admin/flores/{flor_id}")
async def update_flor(flor_id: int, flor: dict, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    # Construir la query dinámicamente según los campos que nos manden
    set_clauses = []
    params = {"flor_id": flor_id}

    if "imagen_url" in flor:
        flor["imagen_url"] = compress_image_b64(flor["imagen_url"])
        
    if "imagenes_extra" in flor:
        extra_images = flor["imagenes_extra"]
        compressed_extra = []
        if isinstance(extra_images, list):
            for img in extra_images:
                compressed_extra.append(compress_image_b64(img))
        flor["imagenes_extra"] = json.dumps(compressed_extra)
    
    for key, value in flor.items():
        # Fix SQLi: validar el nombre de columna contra la whitelist antes de incluirlo en la query
        if key != 'id' and key in COLUMNAS_FLORES_PERMITIDAS:
            set_clauses.append(f"{key} = :{key}")
            params[key] = value
            
    if not set_clauses:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")
        
    set_clause_str = ", ".join(set_clauses)
    query = text(f"UPDATE flores SET {set_clause_str} WHERE id = :flor_id RETURNING *")
    
    result = db.execute(query, params)
    db.commit()
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Flor no encontrada")
        
    keys = result.keys()
    flor_actualizada = dict(zip(keys, row))
    return flor_actualizada

@app.delete("/api/admin/flores/{flor_id}")
async def delete_flor(flor_id: int, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    if current_admin.rol != "admin":
        raise HTTPException(status_code=403, detail="Ruta protegida por RBAC: Solo los Admins pueden borrar productos")
    db_flor = db.query(FlorDB).filter(FlorDB.id == flor_id).first()
    if not db_flor:
        raise HTTPException(status_code=404, detail="Flor no encontrada")
    db.delete(db_flor)
    db.commit()
    return {"message": "Flor eliminada exitosamente"}

@app.get("/api/admin/accesorios_categorias")
async def get_admin_accesorios_categorias(db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    result = db.execute(text("SELECT id, nombre, icono FROM accesorios_categorias"))
    categorias = [{"id": row[0], "nombre": row[1], "icono": row[2] if len(row) > 2 else None} for row in result]
    return categorias

@app.get("/api/admin/accesorios")
async def get_admin_accesorios(db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    result = db.execute(text("SELECT * FROM accesorios ORDER BY id DESC"))
    keys = result.keys()
    accesorios = [dict(zip(keys, row)) for row in result]
    return accesorios

@app.post("/api/admin/accesorios")
async def create_accesorio(acc: dict, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    query = text("""
        INSERT INTO accesorios (nombre, categoria_id, precio, stock, imagen_data, descripcion, sku) 
        VALUES (:nombre, :categoria_id, :precio, :stock, :imagen_data, :descripcion, :sku)
        RETURNING *
    """)
    result = db.execute(query, {
        "nombre": acc.get("nombre"),
        "categoria_id": acc.get("categoria_id"),
        "precio": acc.get("precio"),
        "stock": acc.get("stock", 0),
        "imagen_data": compress_image_b64(acc.get("imagen_data")) if acc.get("imagen_data") else None,
        "descripcion": acc.get("descripcion"),
        "sku": acc.get("sku")
    })
    db.commit()
    keys = result.keys()
    nuevo_acc = dict(zip(keys, result.fetchone()))
    return nuevo_acc

# Whitelist de columnas permitidas para PATCH accesorios (previene SQL Injection en nombres de columna)
COLUMNAS_ACCESORIOS_PERMITIDAS = {
    "nombre", "categoria_id", "precio", "stock", "imagen_data", "descripcion", "sku"
}

@app.patch("/api/admin/accesorios/{accesorio_id}")
async def update_accesorio(accesorio_id: int, acc: dict, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    set_clauses = []
    params = {"accesorio_id": accesorio_id}

    if "imagen_data" in acc and acc["imagen_data"]:
        acc["imagen_data"] = compress_image_b64(acc["imagen_data"])
    
    for key, value in acc.items():
        # Fix SQLi: validar el nombre de columna contra la whitelist antes de incluirlo en la query
        if key != 'id' and key in COLUMNAS_ACCESORIOS_PERMITIDAS:
            set_clauses.append(f"{key} = :{key}")
            params[key] = value
            
    if not set_clauses:
        raise HTTPException(status_code=400, detail="No se enviaron datos para actualizar")
        
    set_clause_str = ", ".join(set_clauses)
    query = text(f"UPDATE accesorios SET {set_clause_str} WHERE id = :accesorio_id RETURNING *")
    
    result = db.execute(query, params)
    db.commit()
    row = result.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Accesorio no encontrado")
        
    keys = result.keys()
    accesorio_actualizado = dict(zip(keys, row))
    return accesorio_actualizado

@app.delete("/api/admin/accesorios/{accesorio_id}")
async def delete_accesorio(accesorio_id: int, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    if current_admin.rol != "admin":
        raise HTTPException(status_code=403, detail="Ruta protegida por RBAC: Solo los Admins pueden borrar productos")
    db_accesorio = db.query(AccesorioDB).filter(AccesorioDB.id == accesorio_id).first()
    if not db_accesorio:
        raise HTTPException(status_code=404, detail="Accesorio no encontrado")
    db.delete(db_accesorio)
    db.commit()
    return {"message": "Accesorio eliminado exitosamente"}

@app.get("/api/admin/vista_pedidos")
async def get_vista_pedidos(limit: int = None, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    query_str = "SELECT * FROM vista_pedidos ORDER BY fecha_pedido DESC"
    if limit:
        query_str += f" LIMIT {limit}"
    
    result = db.execute(text(query_str))
    keys = result.keys()
    
    pedidos = []
    for row in result:
        row_dict = dict(zip(keys, row))
        # Formatear datetimes y decimals si es necesario para JSON
        for k, v in row_dict.items():
            if hasattr(v, 'isoformat'):
                row_dict[k] = v.isoformat()
            if isinstance(v, Decimal):
                row_dict[k] = float(v)
        pedidos.append(row_dict)
    
    return pedidos

@app.get("/api/admin/entregas_pendientes")
async def get_entregas_pendientes(db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    query = text("SELECT * FROM vista_pedidos WHERE estado IN ('pendiente', 'en_camino') ORDER BY fecha_pedido ASC")
    result = db.execute(query)
    keys = result.keys()
    
    entregas = []
    for row in result:
        row_dict = dict(zip(keys, row))
        for k, v in row_dict.items():
            if hasattr(v, 'isoformat'):
                row_dict[k] = v.isoformat()
            if isinstance(v, Decimal):
                row_dict[k] = float(v)
        entregas.append(row_dict)
    
    return entregas

@app.get("/api/admin/resumen_ventas_diario")
async def get_resumen_ventas(limit: int = None, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    query_str = "SELECT * FROM resumen_ventas_diario ORDER BY dia DESC"
    if limit:
        query_str += f" LIMIT {limit}"
        
    result = db.execute(text(query_str))
    keys = result.keys()
    
    ventas = []
    for row in result:
        row_dict = dict(zip(keys, row))
        for k, v in row_dict.items():
            if hasattr(v, 'isoformat'):
                row_dict[k] = v.isoformat()
            if isinstance(v, Decimal):
                row_dict[k] = float(v)
        ventas.append(row_dict)
        
    return ventas

# ================================================================
#  NUEVAS RUTAS FRONTEND PRIVADAS (USUARIO / SETTINGS)
# ================================================================

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

class PreferencesUpdateRequest(BaseModel):
    tema: str
    idioma: str

def parse_user_agent(ua_string: str) -> str:
    if not ua_string: 
        return "Dispositivo Desconocido"
    ua = ua_string.lower()
    os = "Windows" if "windows" in ua else "Mac" if "mac" in ua else "Linux" if "linux" in ua else "Android" if "android" in ua else "iOS" if "iphone" in ua or "ipad" in ua else "Otro OS"
    browser = "Chrome" if "chrome" in ua and "edg" not in ua else "Edge" if "edg" in ua else "Firefox" if "firefox" in ua else "Safari" if "safari" in ua else "Otro Navegador"
    return f"{os} - {browser}"

@app.put("/api/users/me/password")
async def change_password(req: PasswordChangeRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    if not verify_password(req.old_password, current_user.password):
        raise HTTPException(status_code=400, detail="La contraseña actual es incorrecta")
    
    current_user.password = get_password_hash(req.new_password)
    db.commit()
    return {"message": "Contraseña actualizada exitosamente"}

@app.post("/api/users/me/mfa/toggle")
async def toggle_mfa(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # Si esta habilitado, lo deshabilita. (Para habilitar, usan setup-totp existente)
    if current_user.mfa_enabled:
        current_user.mfa_enabled = False
        current_user.mfa_secret = None
        db.commit()
        return {"message": "MFA deshabilitado correctamente"}
    else:
        # Esto solo lo llaman para apagar, para encender, es en el otro endpoint.
        raise HTTPException(status_code=400, detail="Para activar MFA debe configurar el código QR.")

@app.get("/api/users/me/sessions")
async def get_user_sessions(request: Request, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    token = request.cookies.get("refresh_token")
    current_jti = None
    if token:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            current_jti = payload.get("jti")
        except:
            pass
            
    sessions = db.query(SessionDB).filter(
        SessionDB.account_id == current_user.id,
        SessionDB.account_type == "user",
        SessionDB.is_revoked == False,
        SessionDB.expires_at > datetime.utcnow()
    ).all()
    
    return [
        {
            "id": str(s.id),
            "ip_address": s.ip_address or "IP Oculta",
            "device": parse_user_agent(s.user_agent),
            "created_at": s.created_at,
            "expires_at": s.expires_at,
            "is_current": s.refresh_token_jti == current_jti
        } 
        for s in sessions
    ]

@app.delete("/api/users/me/sessions/{session_id}")
async def revoke_remote_session(session_id: str, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_session = db.query(SessionDB).filter(SessionDB.id == session_id, SessionDB.account_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    db_session.is_revoked = True
    db.commit()
    return {"message": "Sesión revocada exitosamente"}

@app.put("/api/users/me/preferences")
async def update_preferences(req: PreferencesUpdateRequest, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    current_user.tema = req.tema
    current_user.idioma = req.idioma
    db.commit()
    return {"message": "Preferencias actualizadas", "tema": current_user.tema, "idioma": current_user.idioma}

@app.get("/api/users/me/preferences")
async def get_preferences(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return {"tema": current_user.tema, "idioma": current_user.idioma, "mfa_enabled": current_user.mfa_enabled}

@app.get("/api/user/direcciones", response_model=list[DireccionResponse])
async def get_user_direcciones(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    return db.query(DireccionDB).filter(DireccionDB.user_id == current_user.id).all()

@app.post("/api/user/direcciones", response_model=DireccionResponse)
async def create_user_direccion(direccion: DireccionCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    count = db.query(DireccionDB).filter(DireccionDB.user_id == current_user.id).count()
    if count >= 4:
        raise HTTPException(status_code=400, detail="El usuario ya tiene un maximo de 4 direcciones permitidas")
    
    if direccion.es_principal:
        db.query(DireccionDB).filter(DireccionDB.user_id == current_user.id).update({"es_principal": False})
    
    db_dir = DireccionDB(**direccion.model_dump(), user_id=current_user.id)
    db.add(db_dir)
    try:
        db.commit()
        db.refresh(db_dir)
        return db_dir
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/user/direcciones/{dir_id}/principal")
async def set_principal_direccion(dir_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_dir = db.query(DireccionDB).filter(DireccionDB.id == dir_id, DireccionDB.user_id == current_user.id).first()
    if not db_dir:
        raise HTTPException(status_code=404, detail="Direccion no encontrada")
    
    db.query(DireccionDB).filter(DireccionDB.user_id == current_user.id).update({"es_principal": False})
    db_dir.es_principal = True
    db.commit()
    return {"message": "Direccion principal actualizada"}

@app.delete("/api/user/direcciones/{dir_id}")
async def delete_user_direccion(dir_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_dir = db.query(DireccionDB).filter(DireccionDB.id == dir_id, DireccionDB.user_id == current_user.id).first()
    if not db_dir:
        raise HTTPException(status_code=404, detail="Direccion no encontrada")
    db.delete(db_dir)
    db.commit()
    return {"message": "Direccion eliminada"}

# ================================================================
#  NUEVAS RUTAS FRONTEND PRIVADAS (CARRITO DE COMPRAS)
# ================================================================

@app.get("/api/user/carrito")
async def get_user_cart(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    try:
        # 1. Obtener o crear el carrito del usuario
        query_cart = text("SELECT * FROM carrito WHERE user_id = :user_id")
        result_cart = db.execute(query_cart, {"user_id": current_user.id}).fetchone()
        
        if not result_cart:
            query_insert = text("INSERT INTO carrito (user_id) VALUES (:user_id) RETURNING *")
            result_cart = db.execute(query_insert, {"user_id": current_user.id}).fetchone()
            db.commit()
            
        carrito_id = result_cart[0]

        # 2. Obtener los items del carrito con la info (Join con flores y accesorios)
        query_items = text("""
            SELECT 
                ci.id as item_id, 
                ci.cantidad,
                f.id as flor_id, f.nombre as flor_nombre, f.precio as flor_precio, f.imagen_url as flor_imagen,
                a.id as accesorio_id, a.nombre as accesorio_nombre, a.precio as accesorio_precio, a.imagen_data as accesorio_imagen
            FROM carrito_items ci
            LEFT JOIN flores f ON ci.flor_id = f.id
            LEFT JOIN accesorios a ON ci.accesorio_id = a.id
            WHERE ci.carrito_id = :carrito_id
            ORDER BY ci.added_at ASC
        """)
        result_items = db.execute(query_items, {"carrito_id": carrito_id})
        keys = result_items.keys()
        
        items_formateados = []
        for row in result_items:
            row_dict = dict(zip(keys, row))
            
            # Determine si es flor o accesorio
            if row_dict["flor_id"]:
                item_data = {
                    "id": row_dict["item_id"],
                    "tipo": "flor",
                    "producto_id": row_dict["flor_id"],
                    "nombre": row_dict["flor_nombre"],
                    "precio": float(row_dict["flor_precio"]) if row_dict["flor_precio"] else 0.0,
                    "imagen": row_dict["flor_imagen"],
                    "cantidad": row_dict["cantidad"]
                }
            elif row_dict["accesorio_id"]:
                item_data = {
                    "id": row_dict["item_id"],
                    "tipo": "accesorio",
                    "producto_id": row_dict["accesorio_id"],
                    "nombre": row_dict["accesorio_nombre"],
                    "precio": float(row_dict["accesorio_precio"]) if row_dict["accesorio_precio"] else 0.0,
                    "imagen": row_dict["accesorio_imagen"],
                    "cantidad": row_dict["cantidad"]
                }
            else:
                continue
                
            items_formateados.append(item_data)

        return {
            "carrito_id": carrito_id,
            "items": items_formateados
        }
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"Backend Error: {str(e)} | Type: {type(e).__name__} | Trace: {tb[-200:]}")

@app.post("/api/user/carrito/items")
async def add_item_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    try:
        if not item.flor_id and not item.accesorio_id:
            raise HTTPException(status_code=400, detail="Debe especificar una flor_id o accesorio_id")
        if item.flor_id and item.accesorio_id:
            raise HTTPException(status_code=400, detail="Especifique sólo una flor_id o accesorio_id, no ambos")
            
        # Obtener el carrito
        query_cart = text("SELECT id FROM carrito WHERE user_id = :user_id")
        cart_row = db.execute(query_cart, {"user_id": current_user.id}).fetchone()
        
        if not cart_row:
            query_insert = text("INSERT INTO carrito (user_id) VALUES (:user_id) RETURNING id")
            cart_row = db.execute(query_insert, {"user_id": current_user.id}).fetchone()
            db.commit()
        
        carrito_id = cart_row[0]

        # Verificar si el item ya existe en el carrito
        if item.flor_id:
            query_check = text("SELECT id, cantidad FROM carrito_items WHERE carrito_id = :carrito_id AND flor_id = :flor_id")
            params = {"carrito_id": carrito_id, "flor_id": item.flor_id}
        else:
            query_check = text("SELECT id, cantidad FROM carrito_items WHERE carrito_id = :carrito_id AND accesorio_id = :accesorio_id")
            params = {"carrito_id": carrito_id, "accesorio_id": item.accesorio_id}
            
        existing_item = db.execute(query_check, params).fetchone()

        if existing_item:
            # Si existe, sumamos la cantidad
            nueva_cantidad = existing_item[1] + item.cantidad
            query_update = text("UPDATE carrito_items SET cantidad = :cantidad WHERE id = :id RETURNING *")
            db.execute(query_update, {"cantidad": nueva_cantidad, "id": existing_item[0]})
            db.commit()
            return {"message": "Cantidad actualizada en el carrito", "item_id": existing_item[0]}
        else:
            # Si no existe, lo insertamos
            query_insert_item = text("""
                INSERT INTO carrito_items (carrito_id, flor_id, accesorio_id, cantidad) 
                VALUES (:carrito_id, :flor_id, :accesorio_id, :cantidad) RETURNING *
            """)
            insert_params = {
                "carrito_id": carrito_id, 
                "flor_id": item.flor_id, 
                "accesorio_id": item.accesorio_id, 
                "cantidad": item.cantidad
            }
            new_item = db.execute(query_insert_item, insert_params).fetchone()
            db.commit()
            return {"message": "Item agregado al carrito", "item_id": new_item[0]}
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=400, detail=f"Backend Error: {str(e)} | Type: {type(e).__name__} | Trace: {tb[-200:]}")

@app.patch("/api/user/carrito/items/{item_id}")
async def update_cart_item(item_id: int, payload: CartItemUpdate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    # Primero verificamos que este item pertenezca al carrito del usuario
    query_check = text("""
        SELECT ci.id FROM carrito_items ci 
        JOIN carrito c ON ci.carrito_id = c.id 
        WHERE ci.id = :item_id AND c.user_id = :user_id
    """)
    if not db.execute(query_check, {"item_id": item_id, "user_id": current_user.id}).fetchone():
        raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
        
    query_update = text("UPDATE carrito_items SET cantidad = :cantidad WHERE id = :item_id RETURNING *")
    db.execute(query_update, {"cantidad": payload.cantidad, "item_id": item_id})
    db.commit()
    return {"message": "Cantidad actualizada"}

@app.delete("/api/user/carrito/items/{item_id}")
async def delete_cart_item(item_id: int, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    query_check = text("""
        SELECT ci.id FROM carrito_items ci 
        JOIN carrito c ON ci.carrito_id = c.id 
        WHERE ci.id = :item_id AND c.user_id = :user_id
    """)
    if not db.execute(query_check, {"item_id": item_id, "user_id": current_user.id}).fetchone():
        raise HTTPException(status_code=404, detail="Item no encontrado en el carrito")
        
    query_delete = text("DELETE FROM carrito_items WHERE id = :item_id")
    db.execute(query_delete, {"item_id": item_id})
    db.commit()
    return {"message": "Item eliminado del carrito"}

from auth_extras import router as auth_extras_router
app.include_router(auth_extras_router)

# --- INCLUSIÓN DE MICROSERVICIOS AISLADOS (PARTE 4, 5 Y 6) ---
from routers.auth_service import router as ms_auth_router
from routers.catalog_service import router as ms_catalog_router
from routers.cart_service import router as ms_cart_router

# Enrutamiento tipo API Gateway Interno
app.include_router(ms_auth_router)
app.include_router(ms_catalog_router)
app.include_router(ms_cart_router)

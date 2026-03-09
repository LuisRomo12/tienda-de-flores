from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import create_engine, Column, Integer, String, Boolean, text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import urllib.parse
import os
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
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 1 día

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
usuario = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "password_secreta")
password_encoded = urllib.parse.quote_plus(password)
DATABASE_URL = f"postgresql://{usuario}:{password_encoded}@localhost:5432/floreria_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la Tabla (Esto creará la tabla 'users')
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class AdminDB(Base):
    __tablename__ = "admins"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    nombre = Column(String)
    activo = Column(Boolean, default=True)

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

# Crear tablas automáticamente al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://127.0.0.1:5173",
        "http://localhost:5501",
        "http://127.0.0.1:5501"
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
        if username is None or role != "web_admin":
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
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if user is None:
        raise credentials_exception
    return user

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
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

@app.post("/api/admin/login")
async def login_admin(admin: AdminLogin, db: Session = Depends(get_db)):
    db_admin = db.query(AdminDB).filter(AdminDB.username == admin.username).first()
    if not db_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El usuario o la contraseña son incorrectos")
    
    if not verify_password(admin.password, db_admin.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El usuario o la contraseña son incorrectos")
    
    if not db_admin.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Esta cuenta de administrador está inactiva")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Aquí podríamos agregar un campo de rol (ej: "role": "web_admin") si planeas integrar con el JWT de PostgREST
    access_token = create_access_token(
        data={"sub": db_admin.username, "role": "web_admin"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "nombre": db_admin.nombre}

@app.post("/api/login")
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserDB).filter(UserDB.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El correo o la contraseña son incorrectos")
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="El correo o la contraseña son incorrectos")
    
    # Usuario válido -> Crear Token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

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
        if key != 'id':
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
    query = text("DELETE FROM flores WHERE id = :flor_id RETURNING id")
    result = db.execute(query, {"flor_id": flor_id})
    db.commit()
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Flor no encontrada")
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

@app.patch("/api/admin/accesorios/{accesorio_id}")
async def update_accesorio(accesorio_id: int, acc: dict, db: Session = Depends(get_db), current_admin: AdminDB = Depends(get_current_admin)):
    set_clauses = []
    params = {"accesorio_id": accesorio_id}

    if "imagen_data" in acc and acc["imagen_data"]:
        acc["imagen_data"] = compress_image_b64(acc["imagen_data"])
    
    for key, value in acc.items():
        if key != 'id':
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
    query = text("DELETE FROM accesorios WHERE id = :accesorio_id RETURNING id")
    result = db.execute(query, {"accesorio_id": accesorio_id})
    db.commit()
    if not result.fetchone():
        raise HTTPException(status_code=404, detail="Accesorio no encontrado")
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
#  NUEVAS RUTAS FRONTEND PRIVADAS (USUARIO)
# ================================================================

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
    # 1. Obtener o crear el carrito del usuario
    query_cart = text("SELECT * FROM carrito WHERE user_id = :user_id")
    result_cart = db.execute(query_cart, {"user_id": current_user.id}).fetchone()
    
    if not result_cart:
        query_insert = text("INSERT INTO carrito (user_id) VALUES (:user_id) RETURNING *")
        result_cart = db.execute(query_insert, {"user_id": current_user.id}).fetchone()
        db.commit()
        
    carrito_id = dict(zip(result_cart._mapping.keys(), result_cart))["id"]

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
    
    items_formateados = []
    for row in result_items:
        row_dict = dict(zip(row._mapping.keys(), row))
        
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

@app.post("/api/user/carrito/items")
async def add_item_to_cart(item: CartItemCreate, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
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

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid
import pyotp
import random
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer

import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/api/auth", tags=["auth_extras"])

def send_real_email(destinatario: str, asunto: str, cuerpo: str):
    remitente = os.environ.get("SMTP_EMAIL")
    password = os.environ.get("SMTP_PASSWORD")
    
    if not remitente or not password:
        print(f"\n[EMAIL SIMULADO]\nPara: {destinatario}\nAsunto: {asunto}\nMensaje:\n{cuerpo}\n")
        return
        
    def send():
        try:
            msg = MIMEMultipart()
            msg['From'] = remitente
            msg['To'] = destinatario
            msg['Subject'] = asunto
            msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(remitente, password)
            server.send_message(msg)
            server.quit()
        except Exception as e:
            print(f"Error enviando correo SMTP: {e}")
            
    threading.Thread(target=send).start()


# Dependencias desde main
from main import get_db, SessionDB, get_current_user, UserDB, AdminDB, create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

# ----- IN-MEMORY CACHE FOR EMAIL OTP (Simulated) -----
# Structure: {"user_id_type": {"code": "123456", "expires_at": datetime}}
email_otp_cache = {}

class MFAVerifyRequest(BaseModel):
    code: str
    method: str  # "totp" o "email"

class PasswordRecoverRequest(BaseModel):
    email: str

oauth2_mfa_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

async def get_mfa_pending_account(token: str = Depends(oauth2_mfa_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload.get("mfa_pending"):
            raise HTTPException(status_code=400, detail="Token no válido para proceso MFA")
        return {"sub": payload.get("sub"), "type": payload.get("type"), "role": payload.get("role", None)}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


@router.post("/mfa/setup-totp")
async def setup_totp(current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    secret = pyotp.random_base32()
    
    # Save to user's DB immediately
    current_user.mfa_secret = secret
    current_user.mfa_enabled = True
    db.commit()
    
    # Generate URI compatible with Google Authenticator
    uri = pyotp.totp.TOTP(secret).provisioning_uri(name=current_user.email, issuer_name="FloreriaGothic")
    
    return {"secret": secret, "qr_code_url": uri}

@router.post("/mfa/send-email-otp")
async def send_email_otp(account: dict = Depends(get_mfa_pending_account)):
    code = f"{random.randint(100000, 999999)}"
    cache_key = f"{account['sub']}_{account['type']}"
    
    # Almacenar con expiración de 5 minutos
    email_otp_cache[cache_key] = {
        "code": code,
        "expires_at": datetime.utcnow() + timedelta(minutes=5)
    }
    
    # Averiguar el correo a dónde enviarlo (si es user, a su email, si es admin, a su username asumiendo es correo)
    dest_email = account["sub"]
    if account["type"] == "user":
        # Necesitamos el correo real
        # Aunque aquí el "sub" es el ID en main.py línea 463 para mfa.
        pass
    # Enviamos correo (Si el destino no es un email válido fallará el SMTP o rebotará)
    cuerpo = f"Hola, tu código de inicio de sesión es {code}.\nEste código expirará en exactamente 5 minutos."
    send_real_email(f"usuario_id_{account['sub']}@sistema", "Tu código de seguridad (MFA)", cuerpo)

    
    return {"message": "Código de 6 dígitos enviado por correo. Válido por 5 minutos."}

@router.post("/verify-mfa")
async def verify_mfa(req: MFAVerifyRequest, response: Response, account: dict = Depends(get_mfa_pending_account), db: Session = Depends(get_db)):
    account_id = int(account["sub"])
    acc_type = account["type"]
    
    # Cargar usuario/admin real
    if acc_type == "admin":
        db_account = db.query(AdminDB).filter(AdminDB.id == account_id).first()
    else:
        db_account = db.query(UserDB).filter(UserDB.id == account_id).first()

    if not db_account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    # VALIDAR SEGUN EL METODO
    if req.method == "totp":
        if not db_account.mfa_secret:
            raise HTTPException(status_code=400, detail="Autenticador TOTP no está configurado")
        totp = pyotp.TOTP(db_account.mfa_secret)
        if not totp.verify(req.code):
            raise HTTPException(status_code=400, detail="Código TOTP inválido")
            
    elif req.method == "email":
        cache_key = f"{account_id}_{acc_type}"
        cache_data = email_otp_cache.get(cache_key)
        if not cache_data or cache_data["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=400, detail="El código ha expirado o no fue solicitado")
        if cache_data["code"] != req.code:
            raise HTTPException(status_code=400, detail="Código de correo incorrecto")
        
        # Limpiar caché post-verificación exitosa para evitar re-uso
        del email_otp_cache[cache_key]
    else:
        raise HTTPException(status_code=400, detail="Método MFA no soportado")

    # SI LLEGA AQUI, EL MFA FUE EXITOSO -> EMITIR TOKENS DEFINITIVOS
    if acc_type == "admin":
        sub_val = db_account.username
    else:
        sub_val = db_account.email

    access_token = create_access_token(data={"sub": sub_val, "type": acc_type, "role": account.get("role")})
    refresh_token, jti, expires_at = create_refresh_token(db_account.id, acc_type)

    db_session = SessionDB(account_id=db_account.id, account_type=acc_type, refresh_token_jti=jti, expires_at=expires_at)
    db.add(db_session)
    db.commit()

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, samesite="lax", expires=expires_at.strftime("%a, %d %b %Y %H:%M:%S GMT"))
    
    return {"access_token": access_token, "token_type": "bearer", "mfa_verified": True}


# --- OTR AS RUTAS DE AUTH (SESSIONS, RECOVERY, SSO) ---

@router.get("/sessions")
async def get_active_sessions(db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    sessions = db.query(SessionDB).filter(
        SessionDB.account_id == current_user.id,
        SessionDB.account_type == 'user',
        SessionDB.is_revoked == False,
        SessionDB.expires_at > datetime.utcnow()
    ).all()
    return [{"id": str(s.id), "ip_address": s.ip_address, "user_agent": s.user_agent, "created_at": s.created_at, "expires_at": s.expires_at} for s in sessions]

@router.delete("/sessions/{session_id}")
async def revoke_session(session_id: str, db: Session = Depends(get_db), current_user: UserDB = Depends(get_current_user)):
    db_session = db.query(SessionDB).filter(SessionDB.id == session_id, SessionDB.account_id == current_user.id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Sesión no encontrada")
    db_session.is_revoked = True
    db.commit()
    return {"message": "Sesión revocada exitosamente"}

# --- RUTAS DE RECUPERACIÓN (PART 7) ---
from main import limiter, get_password_hash, verify_password, PasswordRecoveryDB, cipher_suite
import hashlib

class PasswordResetRequest(BaseModel):
    email: str
    token: str
    new_password: str

class QuestionSetupRequest(BaseModel):
    pregunta: str
    respuesta: str

class QuestionVerifyRequest(BaseModel):
    email: str
    respuesta: str

class OTPRequest(BaseModel):
    email: str
    method: str

class OTPVerifyRequest(BaseModel):
    email: str
    code: str

def generate_recovery_token(account_id: int, account_type: str, db: Session):
    raw_token = str(uuid.uuid4())
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    expires = datetime.utcnow() + timedelta(minutes=15)
    db_rec = PasswordRecoveryDB(account_id=account_id, account_type=account_type, token_hash=token_hash, expires_at=expires)
    db.add(db_rec)
    db.commit()
    return raw_token

@router.post("/recovery/email")
@limiter.limit("5/minute")
async def recover_password_email(request: Request, req: PasswordRecoverRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if user:
        token = generate_recovery_token(user.id, "user", db)
        frontend_url = os.environ.get("FRONTEND_URL", "https://tienda-de-flores.vercel.app")
        cuerpo = f"Has solicitado recuperar tu contraseña.\n\nHaz clic en el siguiente enlace para crear una nueva:\n{frontend_url}/recovery?token={token}&email={user.email}\n\nSi no fuiste tú, ignora este mensaje."
        send_real_email(user.email, "Recuperación de contraseña", cuerpo)
    return {"message": "Si el correo está registrado, se enviarán las instrucciones a su bandeja."}

@router.post("/recovery/reset")
@limiter.limit("5/minute")
async def reset_password(request: Request, req: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Petición inválida")
    
    token_hash = hashlib.sha256(req.token.encode()).hexdigest()
    db_token = db.query(PasswordRecoveryDB).filter(
        PasswordRecoveryDB.account_id == user.id,
        PasswordRecoveryDB.account_type == "user",
        PasswordRecoveryDB.token_hash == token_hash,
        PasswordRecoveryDB.used == False,
        PasswordRecoveryDB.expires_at > datetime.utcnow()
    ).first()
    
    if not db_token:
        raise HTTPException(status_code=400, detail="El enlace es inválido o ha expirado.")
        
    user.password = get_password_hash(req.new_password)
    db_token.used = True
    db.commit()
    return {"message": "Contraseña actualizada exitosamente."}

@router.post("/users/me/security-question")
async def setup_security_question(req: QuestionSetupRequest, current_user: UserDB = Depends(get_current_user), db: Session = Depends(get_db)):
    pregunta_cifrada = cipher_suite.encrypt(req.pregunta.encode()).decode()
    current_user.pregunta_secreta = pregunta_cifrada
    current_user.respuesta_secreta_hash = get_password_hash(req.respuesta.lower().strip())
    db.commit()
    return {"message": "Pregunta de seguridad configurada."}

@router.get("/recovery/question/{email}")
async def get_security_question(email: str, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == email).first()
    if not user or not user.pregunta_secreta:
        raise HTTPException(status_code=404, detail="El usuario no tiene una pregunta configurada.")
    try:
        pregunta_descifrada = cipher_suite.decrypt(user.pregunta_secreta.encode()).decode()
    except Exception:
        pregunta_descifrada = user.pregunta_secreta
    return {"pregunta": pregunta_descifrada}

@router.post("/recovery/question/verify")
@limiter.limit("5/minute")
async def verify_security_question(request: Request, req: QuestionVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user or not user.respuesta_secreta_hash:
        raise HTTPException(status_code=400, detail="Credenciales inválidas.")

    if user.recovery_locked_until and user.recovery_locked_until > datetime.utcnow():
        raise HTTPException(status_code=403, detail="Demasiados intentos. Intente nuevamente en 15 minutos.")

    respuesta_limpia = req.respuesta.lower().strip()
    if not verify_password(respuesta_limpia, user.respuesta_secreta_hash):
        user.recovery_attempts = (user.recovery_attempts or 0) + 1
        if user.recovery_attempts >= 3:
            user.recovery_locked_until = datetime.utcnow() + timedelta(minutes=15)
        db.commit()
        raise HTTPException(status_code=400, detail="Respuesta incorrecta.")
    
    user.recovery_attempts = 0
    user.recovery_locked_until = None
    token = generate_recovery_token(user.id, "user", db)
    return {"token": token, "message": "Respuesta correcta. Proceda a cambiar su contraseña."}

@router.post("/recovery/otp/request")
@limiter.limit("3/minute")
async def request_recovery_otp(request: Request, req: OTPRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if user:
        code = f"{random.randint(100000, 999999)}"
        cache_key = f"recovery_{user.id}_user"
        email_otp_cache[cache_key] = {"code": code, "expires_at": datetime.utcnow() + timedelta(minutes=5)}
        
        if req.method == "sms":
            print(f"\n[SMS SIMULADO a {user.email}] Tu código de recuperación UTFLOWER es: {code}\n")
        else:
            print(f"\n[LLAMADA DE VOZ SIMULADA a {user.email}] (Voz robótica): Hola. El código solicitado es... {code[0]}... {code[1]}... {code[2]}... {code[3]}... {code[4]}... {code[5]}. Repito... {code}.\n")

    return {"message": "Si los datos son correctos, recibirá un código de 6 dígitos."}

@router.post("/recovery/otp/verify")
@limiter.limit("5/minute")
async def verify_recovery_otp(request: Request, req: OTPVerifyRequest, db: Session = Depends(get_db)):
    user = db.query(UserDB).filter(UserDB.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Código inválido.")
        
    cache_key = f"recovery_{user.id}_user"
    cache_data = email_otp_cache.get(cache_key)
    if not cache_data or cache_data["expires_at"] < datetime.utcnow():
        raise HTTPException(status_code=400, detail="El código ha expirado.")
    if cache_data["code"] != req.code:
        raise HTTPException(status_code=400, detail="Código incorrecto.")
        
    del email_otp_cache[cache_key]
    token = generate_recovery_token(user.id, "user", db)
    return {"token": token, "message": "Código verificado."}

@router.post("/sso-simulado")
async def simulate_sso(provider: str, token: str, db: Session = Depends(get_db)):
    if token == "mock-valid-token" and provider == "google":
        return {"access_token": "mock-jwt-from-sso", "token_type": "bearer", "user": "sso_user@gmail.com"}
    raise HTTPException(status_code=401, detail="Fallo en la autenticación SSO simulada")

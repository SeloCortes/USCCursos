from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import os

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from database import SessionLocal
import models


# Usar pbkdf2_sha256 evita la limitación de 72 bytes de bcrypt y es una
# opción segura y ampliamente soportada para nuevas aplicaciones.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Devuelve el hash seguro de una contraseña usando PBKDF2-SHA256."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)


# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "djlqXt67U@%L36bL0$9s6S^Pl8YGrUO")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/iniciar_sesion")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crea un JWT con los claims pasados en `data`.

    - `data` debe ser un dict serializable (ej. {"sub": "123"}).
    - `expires_delta` controla la expiración; si es None se usa el valor por defecto.
    """
    to_encode = data.copy()
    now = datetime.utcnow()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = now + expires_delta
    to_encode.update({"exp": expire, "iat": now})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    # jwt.encode returns a str in PyJWT >=2.x
    return token


def decode_access_token(token: str) -> dict:
    """Decodifica y verifica un token JWT. Lanza HTTPException si es inválido/expirado."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Dependency para FastAPI que devuelve el usuario autenticado a partir del token.

    El token debe contener el claim `sub` con la identificación del usuario (identificacion).
    """
    payload = decode_access_token(token)
    identificacion = payload.get("sub")
    if identificacion is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token sin sujeto")

    # la identificación se guarda como string en el token; convertimos a int si es posible
    try:
        identificacion_int = int(identificacion)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Identificación inválida en token")

    usuario = db.query(models.Usuario).filter(models.Usuario.identificacion == identificacion_int).first()
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return usuario

from passlib.context import CryptContext

# Usar pbkdf2_sha256 evita la limitación de 72 bytes de bcrypt y es una
# opción segura y ampliamente soportada para nuevas aplicaciones.
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    """Devuelve el hash seguro de una contraseña usando PBKDF2-SHA256."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica que una contraseña en texto plano coincide con su hash."""
    return pwd_context.verify(plain_password, hashed_password)

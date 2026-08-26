import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

def get_required_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


SECRET_KEY = get_required_env("SECRET_KEY", "123456789")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Sete dias é o prazo padrão da sessão; a variável permite reduzi-lo por ambiente.
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(7 * 24 * 60)))

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(data: dict):
    payload = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload.update({"exp": expire})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

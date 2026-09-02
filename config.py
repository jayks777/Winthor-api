from fastapi.middleware.cors import CORSMiddleware
from fastapi_mail import ConnectionConfig
from dotenv import load_dotenv
import os
# pyrefly: ignore [missing-import]
from slowapi.errors import RateLimitExceeded
# pyrefly: ignore [missing-import]
from slowapi import _rate_limit_exceeded_handler
# pyrefly: ignore [missing-import]
from utils.limiter import limiter
from starlette.middleware.gzip import GZipMiddleware
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

def configure_all(app):
    configure_cors(app)
    configure_routes(app)
    configure_limiter(app)
    configure_compression(app)

def configure_routes(app):
    from routes.user import router as user_router
    from routes.departments import router as departments_router
    from routes.produtos import router as product_router
    from routes.comunication import router as channel_router
    from routes.auth import router as auth_router
    from routes.clients import router as clients_router
    from routes.prestacoes import router as prestacoes_router
    from routes.usuarios import router as usuarios_router
    from routes.relatorios import router as relatorios_router
    from routes.supervisores import router as supervisores_router
    
    app.include_router(user_router)
    app.include_router(departments_router)
    app.include_router(product_router)
    app.include_router(channel_router)
    app.include_router(auth_router)
    app.include_router(clients_router)
    app.include_router(prestacoes_router)
    app.include_router(usuarios_router)
    app.include_router(relatorios_router)
    app.include_router(supervisores_router)

def configure_cors(app):
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")

    allowed_origins = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]

    if not allowed_origins:
        raise RuntimeError("CORS_ALLOWED_ORIGINS deve conter origens explicitas.")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS", "PATCH", "PUT", "DELETE"],
        allow_headers=["*"],
    )

def configure_compression(app):
    """Comprime respostas grandes (ex.: listas com milhares de prestações).

    compresslevel=1: compressão bem mais rápida que o nível 9 e com taxa
    praticamente igual para JSON (texto repetitivo).
    """
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1024,
        compresslevel=1,
    )
    
def configure_mail_channel():
    conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MAIL_FROM=os.getenv('MAIL_FROM'),
    MAIL_PORT=int(os.getenv('MAIL_PORT')),
    MAIL_SERVER=os.getenv('MAIL_SERVER'),
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,

    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    )
    
    return conf

def configure_limiter(app):
    app.state.limiter = limiter

    app.add_exception_handler(
        RateLimitExceeded,
        _rate_limit_exceeded_handler
    )


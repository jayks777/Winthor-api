from routes.user import router as user_router
from routes.departments import router as departments_router
from fastapi.middleware.cors import CORSMiddleware
import os

def configure_all(app):
    configure_cors(app)
    configure_routes(app)

def configure_routes(app):
    app.include_router(user_router)
    app.include_router(departments_router)

def configure_cors(app):
    raw_origins = os.getenv("CORS_ALLOWED_ORIGINS","*")
    
    # Processa as origens da mesma forma que você fez
    allowed_origins = [
        origin.strip()
        for origin in raw_origins.split(",")
        if origin.strip()
    ]
    
    # Regra crucial: Se houver "*" na lista, allow_credentials DEVE ser False
    # Caso contrário, se houver origens específicas, pode ser True
    allow_credentials = False if "*" in allowed_origins else True

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,  # Ajustado dinamicamente
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
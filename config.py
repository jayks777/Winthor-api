from routes.user import router as user_router
from fastapi.middleware.cors import CORSMiddleware
import os

def configure_all(app):
    configure_cors(app)
    configure_routes(app)

def configure_routes(app):
    app.include_router(user_router)

def configure_cors(app):
    allowed_origins = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,https://4e32-177-190-124-132.ngrok-free.app"
        ).split(",")
        if origin.strip()
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
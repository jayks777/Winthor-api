import os
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from core.auth import ACCESS_TOKEN_COOKIE_NAME, get_current_user
from core.encrypt import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token
from db.uol_database import get_db
from db.schemas import UserLogin, UserResponse
from services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

LOGIN_ATTEMPTS: dict[str, list[float]] = {}
LOGIN_RATE_LIMIT_ATTEMPTS = int(os.getenv("LOGIN_RATE_LIMIT_ATTEMPTS", "5"))
LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("LOGIN_RATE_LIMIT_WINDOW_SECONDS", "300")
)


def check_login_rate_limit(request: Request, usuario: str):
    client_host = request.client.host if request.client else "unknown"
    key = f"{client_host}:{usuario.lower()}"
    now = time.monotonic()
    window_start = now - LOGIN_RATE_LIMIT_WINDOW_SECONDS
    attempts = [
        attempt
        for attempt in LOGIN_ATTEMPTS.get(key, [])
        if attempt >= window_start
    ]

    if len(attempts) >= LOGIN_RATE_LIMIT_ATTEMPTS:
        LOGIN_ATTEMPTS[key] = attempts
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas de login. Tente novamente mais tarde.",
        )

    attempts.append(now)
    LOGIN_ATTEMPTS[key] = attempts
    return key


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        usuario = body.get("usuario") or body.get("username")
        senha = body.get("senha") or body.get("password")
    else:
        form = await request.form()
        usuario = form.get("username") or form.get("usuario")
        senha = form.get("password") or form.get("senha")

    if not usuario or not senha:
        raise HTTPException(status_code=422, detail="Usuário e senha são obrigatórios.")

    rate_limit_key = check_login_rate_limit(request, str(usuario))

    user = AuthService.authenticate_user(db, str(usuario), str(senha))
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais invalidas")

    LOGIN_ATTEMPTS.pop(rate_limit_key, None)

    access_token = create_access_token(data={"sub": user.usuario})

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite=os.getenv("COOKIE_SAMESITE", "lax"),
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Logged in",
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key=ACCESS_TOKEN_COOKIE_NAME)
    return {"message": "Logged out"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

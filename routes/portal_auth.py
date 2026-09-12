import os
import time

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from core.auth import PORTAL_ACCESS_TOKEN_COOKIE_NAME, get_current_client
from core.encrypt import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, verify_password
from db.uol_database import UolClientes, get_db


router = APIRouter(
    prefix="/portal",
    tags=["portal-auth"],
)


LOGIN_ATTEMPTS: dict[str, list[float]] = {}

LOGIN_RATE_LIMIT_ATTEMPTS = int(
    os.getenv("LOGIN_RATE_LIMIT_ATTEMPTS", "5")
)

LOGIN_RATE_LIMIT_WINDOW_SECONDS = int(
    os.getenv("LOGIN_RATE_LIMIT_WINDOW_SECONDS", "300")
)


def check_client_login_rate_limit(
    request: Request,
    numdoc: str,
):
    client_host = request.client.host if request.client else "unknown"

    key = f"portal:{client_host}:{numdoc}"

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
async def client_login(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        body = await request.json()

        numdoc = body.get("numdoc") or body.get("cpf") or body.get("cnpj")
        senha = body.get("senha") or body.get("password")

    else:
        form = await request.form()

        numdoc = (
            form.get("numdoc")
            or form.get("cpf")
            or form.get("cnpj")
        )

        senha = form.get("senha") or form.get("password")

    if not numdoc or not senha:
        raise HTTPException(
            status_code=422,
            detail="CPF/CNPJ e senha são obrigatórios.",
        )

    numdoc = "".join(
        char for char in str(numdoc)
        if char.isdigit()
    )

    if not numdoc:
        raise HTTPException(
            status_code=422,
            detail="CPF/CNPJ inválido.",
        )

    rate_limit_key = check_client_login_rate_limit(
        request,
        numdoc,
    )

    client = (
        db.query(UolClientes)
        .filter(UolClientes.NUMDOC == numdoc)
        .first()
    )

    if not client:
        raise HTTPException(
            status_code=401,
            detail="CPF/CNPJ ou senha inválidos.",
        )

    if not client.PERMISSAO:
        raise HTTPException(
            status_code=403,
            detail="Acesso ao portal não está liberado.",
        )

    if not verify_password(
        str(senha),
        client.SENHA,
    ):
        raise HTTPException(
            status_code=401,
            detail="CPF/CNPJ ou senha inválidos.",
        )

    LOGIN_ATTEMPTS.pop(rate_limit_key, None)

    access_token = create_access_token(
        data={
            "sub": str(client.ID),
            "type": "client",
        }
    )

    response.set_cookie(
        key=PORTAL_ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        samesite=os.getenv("COOKIE_SAMESITE", "lax"),
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login realizado com sucesso.",
    }


@router.post("/logout")
def client_logout(response: Response):
    response.delete_cookie(
        key=PORTAL_ACCESS_TOKEN_COOKIE_NAME
    )

    return {
        "message": "Logout realizado com sucesso."
    }


@router.get("/me")
def client_me(
    current_client: UolClientes = Depends(get_current_client),
):
    return {
        "id": current_client.ID,
        "codcli": current_client.CODCLI,
        "numdoc": current_client.NUMDOC,
        "nome": current_client.NOME,
        "permissao": current_client.PERMISSAO,
    }
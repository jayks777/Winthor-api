from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.encrypt import ALGORITHM, SECRET_KEY
from db.uol_database import UolUser, UolClientes, get_db

ACCESS_TOKEN_COOKIE_NAME = "access_token"
PORTAL_ACCESS_TOKEN_COOKIE_NAME = "portal_access_token"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


def get_current_user(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    token = token or request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(UolUser).filter(UolUser.usuario == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

def get_current_client(
    request: Request,
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    token = token or request.cookies.get(PORTAL_ACCESS_TOKEN_COOKIE_NAME)

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        token_type = payload.get("type")

        if token_type != "client":
            raise HTTPException(
                status_code=401,
                detail="Invalid client token",
            )

        client_id = payload.get("sub")

        if not client_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token",
            )

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )

    client = (
        db.query(UolClientes)
        .filter(UolClientes.ID == int(client_id))
        .first()
    )

    if not client:
        raise HTTPException(
            status_code=401,
            detail="Client not found",
        )

    if not client.PERMISSAO:
        raise HTTPException(
            status_code=403,
            detail="Client access is disabled",
        )

    return client
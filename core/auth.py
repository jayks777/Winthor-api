from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from core.encrypt import ALGORITHM, SECRET_KEY
from db.uol_database import UolUser, get_db

ACCESS_TOKEN_COOKIE_NAME = "access_token"

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
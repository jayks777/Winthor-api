from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.auth import get_current_user
from db.db import get_db
from db.schemas import UsuarioResponse
from repositories.user_repository import UserRepository

router = APIRouter(tags=["Vendedores - Winthor"], prefix="/user")


@router.get("/", response_model=list[UsuarioResponse])
def get_all_users(
    db: Session = Depends(get_db),
    codusur: int | None = None,
    current_user = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    """Retorna todos os vendedores (usuarios) do sistema."""
    return UserRepository.get_all(db, codusur=codusur)
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from db.schemas import UsuarioResponse
from db.db import get_db
from repositories.user_repository import UserRepository
from core.auth import get_current_user  

router = APIRouter(tags=["Usuários - Winthor"], prefix="/user")

@router.get("/", response_model=list[UsuarioResponse])
def get_all_users(
    db: Session = Depends(get_db),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    codusur: int | None = None,
    current_user = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    """Retorna uma lista paginada de todos os vendedores (usuários) do sistema.

    Args:
        db: Sessão do banco de dados
        limit: Número máximo de usuários por página
        offset: Índice de início da paginação
    """
    users = UserRepository.get_all(db, limit=limit, offset=offset)
    return users



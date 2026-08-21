from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.auth import get_current_user
from db.db import get_db
from db.schemas import ClienteComPrestacoes, ClienteResponse
from db.uol_database import UolUser
from repositories.client_repository import ClientRepository

router = APIRouter(prefix="/clients", tags=["Clientes"])


@router.get("/", response_model=list[ClienteResponse])
def list_clients(
    search: str | None = Query(default=None, description="Busca por nome ou codigo do cliente"),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna todos os clientes cadastrados no WinThor (com busca opcional)."""
    return ClientRepository.find_all(db, search=search)


@router.get("/{codcli}", response_model=ClienteResponse)
def get_client(
    codcli: int,
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna os dados de um cliente específico pelo código."""
    client = ClientRepository.find_by_id(db, codcli)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return client


@router.get("/{codcli}/prestacoes", response_model=ClienteComPrestacoes)
def get_client_prestacoes(
    codcli: int,
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna os dados do cliente junto com todas as suas prestações (contas a receber)."""
    client = ClientRepository.find_by_id(db, codcli)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    prestacoes = ClientRepository.find_prestacoes(db, codcli)
    return {
        "CODCLI": client.CODCLI,
        "CLIENTE": client.CLIENTE,
        "CGCENT": client.CGCENT,
        "ENDERENT": client.ENDERENT,
        "MUNICENT": client.MUNICENT,
        "TELENT": client.TELENT,
        "LIMCRED": client.LIMCRED,
        "IEENT": client.IEENT,
        "prestacoes": prestacoes,
    }
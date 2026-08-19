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
    search: str | None = Query(default=None, description="Busca por nome ou código do cliente"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna lista de clientes cadastrados no WinThor com busca e paginação."""
    return ClientRepository.find_all(db, search=search, limit=limit, offset=offset)


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
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna os dados do cliente junto com suas prestações (contas a receber)."""
    client = ClientRepository.find_by_id(db, codcli)
    if not client:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    prestacoes = ClientRepository.find_prestacoes(db, codcli, limit=limit, offset=offset)
    return {
        "CODCLI": client.CODCLI,
        "CLIENTE": client.CLIENTE,
        "CGCCLI": client.CGCCLI,
        "ENDCLI": client.ENDCLI,
        "MUNICCOB": client.MUNICCOB,
        "TELEFONE": client.TELEFONE,
        "LIMCRED": client.LIMCRED,
        "BLOQUEIO": client.BLOQUEIO,
        "prestacoes": prestacoes,
    }


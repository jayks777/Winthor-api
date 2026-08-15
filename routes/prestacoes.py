from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.auth import get_current_user
from db.db import get_db
from db.schemas import PrestacaoResponse
from db.uol_database import UolUser
from repositories.prestacao_repository import PrestacaoRepository

router = APIRouter(prefix="/prestacoes", tags=["Prestações"])

# TODO: Fazer o relacionamento entre prestacoes e clientes para trazer o nome do cliente junto com as prestações
# TODO: Trazer o código do vendedor junto com as prestações
# TODO: Trazer a observação junto com as prestações (Banco da uol)
# TODO: Implementar um endpoint de edição das observações (Banco da uol)
# TODO: Fazer o select das prestações

@router.get("/", response_model=list[PrestacaoResponse])
def list_prestacoes(
    codcli: int | None = Query(default=None, description="Filtrar por código do cliente"),
    codfilial: int | None = Query(default=None, description="Filtrar por código da filial"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna lista de prestações (contas a receber) com filtros e paginação."""
    return PrestacaoRepository.find_all(db, codcli=codcli, codfilial=codfilial, limit=limit, offset=offset)


@router.get("/vencidas", response_model=list[PrestacaoResponse])
def list_prestacoes_vencidas(
    codcli: int | None = Query(default=None, description="Filtrar por código do cliente"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna apenas as prestações vencidas e em aberto (sem data de pagamento)."""
    return PrestacaoRepository.find_vencidas(db, codcli=codcli, limit=limit, offset=offset)


@router.get("/a-vencer", response_model=list[PrestacaoResponse])
def list_prestacoes_a_vencer(
    dias: int = Query(default=30, ge=1, le=365, description="Número de dias futuros a considerar"),
    codcli: int | None = Query(default=None, description="Filtrar por código do cliente"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna as prestações a vencer nos próximos N dias (sem data de pagamento)."""
    return PrestacaoRepository.find_a_vencer(db, dias=dias, codcli=codcli, limit=limit, offset=offset)

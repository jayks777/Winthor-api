from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.auth import get_current_user
from db.db import get_db
from db.schemas import PrestacaoObservacaoUpdate, PrestacaoPorDiaResponse, PrestacaoResponse
from db.uol_database import UolUser, get_db as get_uol_db
from repositories.prestacao_repository import PrestacaoRepository

router = APIRouter(prefix="/prestacoes", tags=["Prestações"])


def _with_observacoes(prestacoes, uol_db: Session):
    observacoes = PrestacaoRepository.observacoes_por_duplicata(
        uol_db, [prestacao.DUPLIC for prestacao in prestacoes]
    )
    return PrestacaoRepository.serialize(prestacoes, observacoes)


@router.get("/", response_model=list[PrestacaoResponse])
def list_prestacoes(
    codcli: int | None = Query(default=None, description="Filtrar por código do cliente"),
    codfilial: int | None = Query(default=None, description="Filtrar por código da filial"),
    dias_passados: int = Query(default=30, ge=0, le=365, description="Dias anteriores ao vencimento a considerar"),
    dias_futuros: int = Query(default=30, ge=0, le=365, description="Dias futuros ao vencimento a considerar"),
    search: str | None = Query(default=None, description="Busca por nome do cliente ou número da duplicata (parcial, case-insensitive)"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    uol_db: Session = Depends(get_uol_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna prestações paginadas no intervalo de vencimento solicitado."""
    prestacoes = PrestacaoRepository.find_all(
        db, codcli, codfilial, dias_passados, dias_futuros, limit, offset, search
    )
    return _with_observacoes(prestacoes, uol_db)


@router.get("/vencidas", response_model=list[PrestacaoResponse])
def list_prestacoes_vencidas(
    dias: int = Query(default=30, ge=1, le=365, description="Dias anteriores a considerar"),
    codcli: int | None = Query(default=None, description="Filtrar por código do cliente"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    uol_db: Session = Depends(get_uol_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna prestações em aberto vencidas nos últimos N dias."""
    prestacoes = PrestacaoRepository.find_vencidas(db, dias, codcli, limit, offset)
    return _with_observacoes(prestacoes, uol_db)


@router.get("/a-vencer", response_model=list[PrestacaoResponse])
def list_prestacoes_a_vencer(
    dias: int = Query(default=30, ge=1, le=365, description="Número de dias futuros a considerar"),
    codcli: int | None = Query(default=None, description="Filtrar por código do cliente"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    uol_db: Session = Depends(get_uol_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna prestações em aberto que vencem nos próximos N dias."""
    prestacoes = PrestacaoRepository.find_a_vencer(db, dias, codcli, limit, offset)
    return _with_observacoes(prestacoes, uol_db)


@router.get("/a-vencer/por-dia", response_model=list[PrestacaoPorDiaResponse])
def list_prestacoes_a_vencer_por_dia(
    dias: int = Query(default=30, ge=1, le=365, description="Número de dias futuros (máx. 365)"),
    codfilial: int | None = Query(default=None, description="Filtrar por filial (opcional)"),
    db: Session = Depends(get_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Retorna o total a receber e a quantidade de prestações agrupados por data de vencimento.

    Inclui todos os dias do intervalo, mesmo aqueles sem vencimentos (total=0, quantidade=0).
    Muito mais eficiente que paginar /a-vencer e somar no cliente.
    """
    return PrestacaoRepository.find_a_vencer_por_dia(db, dias, codfilial)


@router.patch("/{duplic}/observacao", response_model=PrestacaoResponse)
def update_prestacao_observacao(
    duplic: int,
    payload: PrestacaoObservacaoUpdate,
    db: Session = Depends(get_db),
    uol_db: Session = Depends(get_uol_db),
    current_user: UolUser = Depends(get_current_user),
):
    """Cria ou atualiza a observação UOL de uma prestação existente."""
    prestacao = PrestacaoRepository.find_by_duplic(db, duplic)
    if prestacao is None:
        raise HTTPException(status_code=404, detail="Prestação não encontrada")

    observacao = payload.observacao.strip()
    if not observacao:
        raise HTTPException(status_code=422, detail="A observação não pode estar vazia")

    PrestacaoRepository.upsert_observacao(uol_db, duplic, observacao)
    return PrestacaoRepository.serialize([prestacao], {duplic: observacao})[0]

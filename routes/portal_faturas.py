from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.auth import get_current_client
from core.settings import apply_max_results
from db.db import get_db
from db.models import Prestacoes
from db.uol_database import UolClientes


router = APIRouter(prefix="/portal/me/faturas", tags=["Portal - Faturas"])


def _serialize(prestacao: Prestacoes, situacao: str) -> dict:
    """Campos de uma fatura que podem ser expostos ao próprio cliente."""
    return {
        "duplicata": prestacao.DUPLIC,
        "parcela": prestacao.PREST,
        "valor": prestacao.VALOR,
        "vencimento": prestacao.DTVENC,
        "emissao": prestacao.DTEMISSAO,
        "pagamento": prestacao.DTBAIXA,
        "codigo_cobranca": prestacao.CODCOB,
        "filial": prestacao.CODFILIAL,
        "pedido": prestacao.NUMPED,
        "situacao": situacao,
    }


def _faturas_do_cliente(db: Session, codcli: int, situacao: str):
    """Nunca recebe CODCLI do request: o escopo vem exclusivamente do JWT."""
    hoje = date.today()
    query = db.query(Prestacoes).filter(Prestacoes.CODCLI == codcli)

    if situacao == "vencidas":
        query = query.filter(
            Prestacoes.DTBAIXA.is_(None),
            Prestacoes.DTVENC < hoje,
        ).order_by(Prestacoes.DTVENC.asc(), Prestacoes.DUPLIC, Prestacoes.PREST)
    elif situacao == "a-vencer":
        query = query.filter(
            Prestacoes.DTBAIXA.is_(None),
            Prestacoes.DTVENC >= hoje,
        ).order_by(Prestacoes.DTVENC.asc(), Prestacoes.DUPLIC, Prestacoes.PREST)
    else:
        query = query.filter(Prestacoes.DTBAIXA.is_not(None)).order_by(
            Prestacoes.DTBAIXA.desc(), Prestacoes.DUPLIC, Prestacoes.PREST
        )

    return [
        _serialize(prestacao, situacao)
        for prestacao in apply_max_results(query).all()
    ]


@router.get("/vencidas")
def faturas_vencidas(
    current_client: UolClientes = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Faturas em aberto com vencimento anterior a hoje, apenas do cliente logado."""
    return _faturas_do_cliente(db, current_client.CODCLI, "vencidas")


@router.get("/a-vencer")
def faturas_a_vencer(
    current_client: UolClientes = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Faturas em aberto, inclusive as que vencem hoje, do cliente logado."""
    return _faturas_do_cliente(db, current_client.CODCLI, "a-vencer")


@router.get("/pagas")
def faturas_pagas(
    current_client: UolClientes = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Faturas baixadas/pagas do cliente logado."""
    return _faturas_do_cliente(db, current_client.CODCLI, "pagas")

import os

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.auth import get_current_client
from db.db import get_db
from db.models import ItensPedido, Pedidos, Produtos
from db.uol_database import UolClientes


router = APIRouter(
    tags=["Portal - Pedidos"],
    prefix="/portal/me",
)


EMPRESA_ID = os.getenv("ISA_ID")


def _imagem_produto(codprod: int | None) -> str | None:
    if codprod is None or not EMPRESA_ID:
        return None
    return f"https://isa-public.s3.amazonaws.com/product-{EMPRESA_ID}-{codprod}.png"


def _serialize_pedido(pedido: Pedidos, itens: list[dict]) -> dict:
    # Não expomos total: a semântica de frete, outras despesas e bonificação
    # precisa ser validada no WinThor antes de consolidar valores por pedido.
    return {
        "numero": pedido.NUMPED,
        "data": pedido.DATA,
        "cancelado_em": pedido.DTCANCEL,
        "filial": pedido.CODFILIAL,
        "condicao_venda": pedido.CONDVENDA,
        "itens": itens,
    }


def _itens_por_pedido(
    db: Session,
    numeros_pedido: list[int],
    codcli: int,
) -> dict[int, list[dict]]:
    if not numeros_pedido:
        return {}

    rows = (
        db.query(
            ItensPedido.NUMPED,
            ItensPedido.NUMSEQ,
            ItensPedido.CODPROD,
            ItensPedido.QT,
            ItensPedido.PVENDA,
            ItensPedido.VLOUTRASDESP,
            ItensPedido.VLFRETE,
            ItensPedido.BONIFIC,
            Produtos.DESCRICAO.label("descricao"),
            Produtos.EMBALAGEM.label("embalagem"),
            Produtos.UNIDADE.label("unidade"),
        )
        .outerjoin(Produtos, Produtos.CODPROD == ItensPedido.CODPROD)
        .filter(
            ItensPedido.NUMPED.in_(numeros_pedido),
            ItensPedido.CODCLI == codcli,
        )
        .order_by(ItensPedido.NUMPED.desc(), ItensPedido.NUMSEQ)
        .all()
    )

    itens: dict[int, list[dict]] = {numero: [] for numero in numeros_pedido}
    for row in rows:
        itens.setdefault(row.NUMPED, []).append({
            "sequencia": row.NUMSEQ,
            "codigo_produto": row.CODPROD,
            "descricao": row.descricao,
            "embalagem": row.embalagem,
            "unidade": row.unidade,
            "quantidade": row.QT,
            "preco_unitario": row.PVENDA,
            "outras_despesas": row.VLOUTRASDESP,
            "frete": row.VLFRETE,
            "bonificacao": row.BONIFIC,
            "imagem": _imagem_produto(row.CODPROD),
        })
    return itens


@router.get("/pedidos")
def client_pedidos(
    limite: int = Query(default=50, ge=1, le=100),
    pagina: int = Query(default=1, ge=1),
    current_client: UolClientes = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Pedidos e itens do cliente autenticado; CODCLI não é aceito como parâmetro."""
    pedidos = (
        db.query(Pedidos)
        .filter(Pedidos.CODCLI == current_client.CODCLI)
        .order_by(Pedidos.DATA.desc())
        .offset((pagina - 1) * limite)
        .limit(limite)
        .all()
    )

    itens = _itens_por_pedido(
        db,
        [pedido.NUMPED for pedido in pedidos],
        current_client.CODCLI,
    )
    return [
        _serialize_pedido(pedido, itens.get(pedido.NUMPED, []))
        for pedido in pedidos
    ]


@router.get("/pedidos/{numped}")
def client_pedido(
    numped: int,
    current_client: UolClientes = Depends(get_current_client),
    db: Session = Depends(get_db),
):
    """Detalhe de um pedido, protegido contra acesso a pedidos de outro cliente."""
    pedido = (
        db.query(Pedidos)
        .filter(
            Pedidos.NUMPED == numped,
            Pedidos.CODCLI == current_client.CODCLI,
        )
        .first()
    )
    if pedido is None:
        # Não revela se o número pertence a outro cliente.
        raise HTTPException(status_code=404, detail="Pedido não encontrado.")

    itens = _itens_por_pedido(db, [pedido.NUMPED], current_client.CODCLI)
    return _serialize_pedido(pedido, itens.get(pedido.NUMPED, []))

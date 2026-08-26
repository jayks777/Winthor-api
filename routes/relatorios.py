from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db.db import get_db
from core.permissions import require_roles
from db.models import (
    Pedidos,
    ItensPedido,
    Vendedores,
    Produtos,
    Clientes,
)
from db.schemas import VendaPorVendedorResponse

router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"]
)


@router.get(
    "/vendas-por-vendedor",
    response_model=list[VendaPorVendedorResponse],
    dependencies=[Depends(require_roles("admin"))]
)
def vendas_por_vendedor(
    datai: date = Query(...),
    dataf: date = Query(...),
    codfilial: int = Query(1),
    db: Session = Depends(get_db)
):
    
    valor_venda = func.round(
        func.nvl(ItensPedido.QT, 0)
        * (
            func.nvl(ItensPedido.PVENDA, 0)
            + func.nvl(ItensPedido.VLOUTRASDESP, 0)
            + func.nvl(ItensPedido.VLFRETE, 0)
        ),
        2
    )

    peso_total = func.round(
        func.nvl(Produtos.PESOBRUTO, 0)
        * func.nvl(ItensPedido.QT, 0),
        2
    )

    stmt = (
        select(
            Pedidos.CODUSUR.label("CODUSUR"),

            Vendedores.NOME.label("NOME"),

            func.count(
                func.distinct(Pedidos.CODCLI)
            ).label("QTCLIPOS"),

            func.sum(valor_venda).label("PVENDA"),

            func.sum(ItensPedido.QT).label("QT"),

            func.sum(peso_total).label("TOTPESO"),
        )

        .select_from(ItensPedido)

        .join(
            Pedidos,
            ItensPedido.NUMPED == Pedidos.NUMPED
        )

        .join(
            Vendedores,
            Pedidos.CODUSUR == Vendedores.CODUSUR
        )

        .join(
            Produtos,
            ItensPedido.CODPROD == Produtos.CODPROD
        )

        .join(
            Clientes,
            Pedidos.CODCLI == Clientes.CODCLI
        )

        .where(
            Vendedores.CODSUPERVISOR != 9999,

            Pedidos.DATA.between(datai, dataf),

            Pedidos.CODFILIAL == codfilial,

            Pedidos.CONDVENDA.in_([
                1, 2, 3, 7, 9,
                14, 15, 17, 18,
                19, 98
            ]),

            func.nvl(
                ItensPedido.BONIFIC,
                "N"
            ) == "N",

            Pedidos.DTCANCEL.is_(None),
        )

        .group_by(
            Pedidos.CODUSUR,
            Vendedores.NOME
        )
    )

    result = db.execute(stmt).mappings().all()

    return result
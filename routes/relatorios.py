from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from db.uol_database import UolUser as User

from db.db import get_db
from core.permissions import require_roles
from core.auth import get_current_user
from db.models import (
    Pedidos,
    ItensPedido,
    Vendedores,
    Produtos,
    Clientes,
    Metas,
)
from core.data_scope import apply_vendedor_scope
from db.schemas import VendaPorVendedorResponse


router = APIRouter(
    prefix="/relatorios",
    tags=["Relatórios"],
)


@router.get(
    "/vendas-por-vendedor",
    response_model=list[VendaPorVendedorResponse],
    dependencies=[Depends(require_roles("admin", "manager", "user"))],
)
def vendas_por_vendedor(
    datai: date = Query(...),
    dataf: date = Query(...),
    codfilial: int = Query(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # ==========================================================
    # SUBQUERY: META POR VENDEDOR NO PERÍODO
    # ==========================================================

    metas_subquery = (
        select(
            Metas.CODUSUR.label("CODUSUR"),
            func.sum(
                Metas.VLVENDAPREV
            ).label("META"),
        )
        .where(
            Metas.DATA.between(datai, dataf)
        )
        .group_by(
            Metas.CODUSUR
        )
        .subquery()
    )

    # ==========================================================
    # CÁLCULO DO VALOR DE VENDA
    # ==========================================================

    valor_venda = func.round(
        func.nvl(ItensPedido.QT, 0)
        * (
            func.nvl(ItensPedido.PVENDA, 0)
            + func.nvl(ItensPedido.VLOUTRASDESP, 0)
            + func.nvl(ItensPedido.VLFRETE, 0)
        ),
        2,
    )

    # ==========================================================
    # CÁLCULO DO PESO
    # ==========================================================

    peso_total = func.round(
        func.nvl(Produtos.PESOBRUTO, 0)
        * func.nvl(ItensPedido.QT, 0),
        2,
    )

    # ==========================================================
    # CONSULTA PRINCIPAL
    # ==========================================================

    stmt = (
        select(
            Pedidos.CODUSUR.label("CODUSUR"),

            Vendedores.NOME.label("NOME"),

            func.count(
                func.distinct(Pedidos.CODCLI)
            ).label("QTCLIPOS"),

            func.sum(
                valor_venda
            ).label("PVENDA"),

            func.sum(
                ItensPedido.QT
            ).label("QT"),

            func.sum(
                peso_total
            ).label("TOTPESO"),

            func.nvl(
                metas_subquery.c.META,
                0,
            ).label("META"),
        )

        .select_from(ItensPedido)

        .join(
            Pedidos,
            ItensPedido.NUMPED == Pedidos.NUMPED,
        )

        .join(
            Vendedores,
            Pedidos.CODUSUR == Vendedores.CODUSUR,
        )

        .join(
            Produtos,
            ItensPedido.CODPROD == Produtos.CODPROD,
        )

        .join(
            Clientes,
            Pedidos.CODCLI == Clientes.CODCLI,
        )

        # Meta do vendedor
        .outerjoin(
            metas_subquery,
            metas_subquery.c.CODUSUR == Pedidos.CODUSUR,
        )

        .where(
            Vendedores.CODSUPERVISOR != 9999,

            Pedidos.DATA.between(
                datai,
                dataf,
            ),

            Pedidos.CODFILIAL == codfilial,

            Pedidos.CONDVENDA.in_([
                1,
                2,
                3,
                7,
                9,
                14,
                15,
                17,
                18,
                19,
                98,
            ]),

            func.nvl(
                ItensPedido.BONIFIC,
                "N",
            ) == "N",

            Pedidos.DTCANCEL.is_(None),
        )

        .group_by(
            Pedidos.CODUSUR,
            Vendedores.NOME,
            metas_subquery.c.META,
        )
    )

    stmt = apply_vendedor_scope(stmt, current_user)

    result = db.execute(
        stmt
    ).mappings().all()

    return result
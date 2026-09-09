from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_
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
    dependencies=[
        Depends(require_roles("admin", "manager", "user"))
    ],
)
def vendas_por_vendedor(
    datai: date = Query(...),
    dataf: date = Query(...),
    codfilial: int = Query(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    data_inicio = datai
    data_fim_exclusivo = dataf + timedelta(days=1)

    metas_subquery = (
        select(
            Metas.CODUSUR.label("CODUSUR"),
            func.sum(
                Metas.VLVENDAPREV
            ).label("META"),
        )
        .where(
            Metas.DATA >= data_inicio,
            Metas.DATA < data_fim_exclusivo,
        )
        .group_by(
            Metas.CODUSUR
        )
        .subquery()
    )

    valor_venda = (
        func.nvl(ItensPedido.QT, 0)
        * (
            func.nvl(ItensPedido.PVENDA, 0)
            + func.nvl(ItensPedido.VLOUTRASDESP, 0)
            + func.nvl(ItensPedido.VLFRETE, 0)
        )
    )

    peso_total = (
        func.nvl(Produtos.PESOBRUTO, 0)
        * func.nvl(ItensPedido.QT, 0)
    )
    
    vendas_subquery = (
        select(
            Pedidos.CODUSUR.label("CODUSUR"),

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
        )

        .select_from(Pedidos)

        .join(
            ItensPedido,
            and_(
                ItensPedido.NUMPED == Pedidos.NUMPED,

                func.nvl(
                    ItensPedido.BONIFIC,
                    "N",
                ) == "N",
            ),
        )

        .join(
            Produtos,
            ItensPedido.CODPROD == Produtos.CODPROD,
        )

        .where(
            Pedidos.DATA >= data_inicio,

            Pedidos.DATA < data_fim_exclusivo,

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

            Pedidos.DTCANCEL.is_(None),
        )

        .group_by(
            Pedidos.CODUSUR,
        )

        .subquery()
    )

    stmt = (
        select(
            Vendedores.CODUSUR.label("CODUSUR"),

            Vendedores.NOME.label("NOME"),

            func.nvl(
                vendas_subquery.c.QTCLIPOS,
                0,
            ).label("QTCLIPOS"),

            func.nvl(
                vendas_subquery.c.PVENDA,
                0,
            ).label("PVENDA"),

            func.nvl(
                vendas_subquery.c.QT,
                0,
            ).label("QT"),

            func.nvl(
                vendas_subquery.c.TOTPESO,
                0,
            ).label("TOTPESO"),

            func.nvl(
                metas_subquery.c.META,
                0,
            ).label("META"),
        )

        .select_from(Vendedores)

        .outerjoin(
            vendas_subquery,
            vendas_subquery.c.CODUSUR
            == Vendedores.CODUSUR,
        )

        .outerjoin(
            metas_subquery,
            metas_subquery.c.CODUSUR
            == Vendedores.CODUSUR,
        )

        .where(
            Vendedores.CODSUPERVISOR != 9999,
        )

        .order_by(
            func.nvl(
                vendas_subquery.c.PVENDA,
                0,
            ).desc()
        )
    )

    stmt = apply_vendedor_scope(
        stmt,
        current_user,
    )

    result = (
        db.execute(stmt)
        .mappings()
        .all()
    )

    return result
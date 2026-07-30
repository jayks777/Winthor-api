from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from db.db import get_db
from db.models import Produtos, Categorias, Departamentos
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(tags=["Geral"])

EMPRESA_ID = os.getenv('ISA_ID')


@router.get("/catalog")
async def catalog(
    db: Session = Depends(get_db),
    codepto: int | None = Query(default=None),
    codsec: int | None = Query(default=None),
    busca: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=32, ge=1, le=100),
):
    '''Retorna produtos do banco WinThor, com categoria/departamento via join
    (sem N+1) e imagem registrada na iSA. Sem filtro: pagina de 32 em 32.
    Com departamento + categoria selecionados: retorna tudo de uma vez.'''

    query = (
        db.query(
            Produtos.CODPROD,
            Produtos.DESCRICAO,
            Produtos.EMBALAGEM,
            Produtos.UNIDADE,
            Categorias.DESCRICAO.label("CATEGORIA"),
            Departamentos.DESCRICAO.label("DEPARTAMENTO"),
        )
        .join(Categorias, Produtos.CODSEC == Categorias.CODSEC)
        .join(Departamentos, Produtos.CODEPTO == Departamentos.CODEPTO)
    )

    if codepto:
        query = query.filter(Produtos.CODEPTO == codepto)

    if codsec:
        query = query.filter(Produtos.CODSEC == codsec)

    if busca:
        termo = f"%{busca.strip()}%"
        query = query.filter(Produtos.DESCRICAO.ilike(termo))

    total = query.count()


    mostrar_tudo = codepto is not None and codsec is not None

    if mostrar_tudo:
        produtos = query.order_by(Produtos.DESCRICAO).all()
    elif busca or codepto or codsec:

        produtos = (
            query.order_by(Produtos.DESCRICAO)
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )
    else:

        produtos = (
            query.order_by(func.dbms_random.value())
            .offset((page - 1) * page_size)
            .limit(page_size)
            .all()
        )

    final_catalog = [
        {
            "CODPROD": p.CODPROD,
            "DESCRICAO": p.DESCRICAO,
            "EMBALAGEM": p.EMBALAGEM,
            "UNIDADE": p.UNIDADE,
            "CATEGORIA": p.CATEGORIA,
            "DEPARTAMENTO": p.DEPARTAMENTO,
            "IMAGEM": f"https://isa-public.s3.amazonaws.com/product-{EMPRESA_ID}-{p.CODPROD}.png",
        }
        for p in produtos
    ]

    return {"total": total, "produtos": final_catalog}
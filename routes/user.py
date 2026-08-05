from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from db.db import get_db
from db.models import Produtos, Categorias, Departamentos, Estoque
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(tags=["Catálogos"])

EMPRESA_ID = os.getenv('ISA_ID')

@router.get("/")
def home():
    return {"status": "Online",
            "Coded by": "Jayks ❤"}

@router.get("/catalog")
async def catalog(
    db: Session = Depends(get_db),
    codepto: int | None = Query(default=None),
    codsec: int | None = Query(default=None),
    busca: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=32, ge=1, le=100),
):
    
    '''Traz um catálogo com imagens do iSA. Não retorna preço e produtos sem estoque'''
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
        .join(Estoque, and_(
            Produtos.CODPROD == Estoque.CODPROD,
            Estoque.CODFILIAL == 1
        )).filter(Estoque.QTEST > 0, Produtos.CODSEC != 110)
    )

    if codepto:
        query = query.filter(Produtos.CODEPTO == codepto)

    if codsec:
        query = query.filter(Produtos.CODSEC == codsec)

    if busca:
        termo = busca.strip()
        if termo.isdigit():

            query = query.filter(Produtos.CODPROD == int(termo))
        else:

            query = query.filter(Produtos.DESCRICAO.ilike(f"%{termo}%"))

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
            query.order_by(Produtos.CODPROD)#func.dbms_random.value()
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
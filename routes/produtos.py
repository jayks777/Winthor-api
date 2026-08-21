from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_
from db.db import get_db
from db.models import Produtos, Categorias, Departamentos, Estoque
from dotenv import load_dotenv
import os
import random

load_dotenv()

router = APIRouter(tags=["Produtos"], prefix="/product")

EMPRESA_ID = os.getenv('ISA_ID')


@router.get("/random")
async def random_product(
    db: Session = Depends(get_db),
):
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
        ))
        .filter(Estoque.QTEST > 0, Produtos.CODSEC != 110)
    )

    total = query.count()
    if total == 0:
        raise HTTPException(status_code=404, detail="Nenhum produto com estoque disponível")

    # Amostragem aleatória barata: evita o ORDER BY dbms_random.value(),
    # que força o Oracle a ordenar o catálogo inteiro em cada chamada.
    offset = random.randrange(total)
    p = query.order_by(Produtos.CODPROD).offset(offset).limit(1).first()

    return {
        "CODPROD": p.CODPROD,
        "DESCRICAO": p.DESCRICAO,
        "EMBALAGEM": p.EMBALAGEM,
        "UNIDADE": p.UNIDADE,
        "CATEGORIA": p.CATEGORIA,
        "DEPARTAMENTO": p.DEPARTAMENTO,
        "IMAGEM": f"https://isa-public.s3.amazonaws.com/product-{EMPRESA_ID}-{p.CODPROD}.png",
    }
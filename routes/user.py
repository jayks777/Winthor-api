from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.db import get_db
from db.models import Produtos
from utils.data import def_cat
from dotenv import load_dotenv
import os

load_dotenv()

router = APIRouter(tags=["user"])

EMPRESA_ID = os.getenv('ISA_ID')

@router.get("/catalog")
async def catalog(db: Session = Depends(get_db)):
    produtos = db.query(Produtos).all()

    final_catalog = []

    for produto in produtos:
        final_catalog.append({
            "CODPROD": produto.CODPROD,
            "DESCRICAO": produto.DESCRICAO,
            "EMBALAGEM": produto.EMBALAGEM,
            "UNIDADE": produto.UNIDADE,
            "CATEGORIA": def_cat(db, produto.CODPROD),
            "IMAGEM": f"https://isa-public.s3.amazonaws.com/product-{EMPRESA_ID}-{produto.CODPROD}.png"
        })

    return final_catalog
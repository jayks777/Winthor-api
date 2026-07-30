from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from db.db import get_db
from db.models import Departamentos, Categorias

router = APIRouter(tags=["Departamentos"], prefix="/departments")

@router.get("/")
async def departments(db: Session = Depends(get_db)):
    '''Retorna todos os departamentos, salvo exessões'''
    departamentos = db.query(Departamentos).all()

    return [
        dp for dp in departamentos
        if 'MIGRACAO' not in dp.DESCRICAO
        and 'TODOS' not in dp.DESCRICAO
    ]

@router.get("/{id}/categories")
async def cat_per_departments(id: int,db: Session = Depends(get_db)):
    '''Retorna as categorias do departamento informado na path'''
    
    return (
        db.query(Categorias)
        .filter(Categorias.CODEPTO == id)
        .order_by(Categorias.DESCRICAO)
        .all()
    )

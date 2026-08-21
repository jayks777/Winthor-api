from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.settings import apply_max_results
from db.db import get_db
from db.models import Categorias, Departamentos

router = APIRouter(tags=["Departamentos"], prefix="/departments")


@router.get("/")
async def departments(
    db: Session = Depends(get_db),
):
    """Retorna todos os departamentos, excluindo os registros especiais."""
    query = (
        db.query(Departamentos)
        .filter(
            ~Departamentos.DESCRICAO.contains("MIGRACAO"),
            ~Departamentos.DESCRICAO.contains("TODOS"),
        )
        .order_by(Departamentos.CODEPTO)
    )
    return apply_max_results(query).all()


@router.get("/{id}/categories")
async def cat_per_departments(
    id: int,
    db: Session = Depends(get_db),
):
    """Retorna todas as categorias do departamento informado."""
    query = (
        db.query(Categorias)
        .filter(Categorias.CODEPTO == id)
        .order_by(Categorias.DESCRICAO, Categorias.CODSEC)
    )
    return apply_max_results(query).all()
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from db.db import get_db
from db.models import Categorias, Departamentos

router = APIRouter(tags=["Departamentos"], prefix="/departments")


@router.get("/")
async def departments(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Retorna departamentos paginados, excluindo os registros especiais."""
    return (
        db.query(Departamentos)
        .filter(
            ~Departamentos.DESCRICAO.contains("MIGRACAO"),
            ~Departamentos.DESCRICAO.contains("TODOS"),
        )
        .order_by(Departamentos.CODEPTO)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{id}/categories")
async def cat_per_departments(
    id: int,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """Retorna categorias paginadas do departamento informado."""
    return (
        db.query(Categorias)
        .filter(Categorias.CODEPTO == id)
        .order_by(Categorias.DESCRICAO, Categorias.CODSEC)
        .offset(offset)
        .limit(limit)
        .all()
    )

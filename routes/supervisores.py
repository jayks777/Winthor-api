from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.permissions import require_roles
from core.auth import get_current_user
from db.db import get_db
from db.schemas import SupervisorResponse
from repositories.manager_repository import SupervisoresRepository

router = APIRouter(tags=["Supervisores - Winthor"], prefix="/manager")


@router.get("/", 
            response_model=list[SupervisorResponse],
            dependencies=[Depends(require_roles("admin", "manager"))]
            )
def get_all_supervisores(
    db: Session = Depends(get_db),
    codsupervisor: int | None = None,
    current_user = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    """Retorna todos os supervisores (usuarios) do sistema."""
    return SupervisoresRepository.get_all(db, codsupervisor=codsupervisor)
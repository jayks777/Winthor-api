from fastapi import HTTPException
from sqlalchemy import Select

from db.models import Vendedores


def apply_vendedor_scope(
    stmt: Select,
    current_user,
):
    role = current_user.role.lower()

    if role in "admin":
        return stmt

    if role == "manager":
        if current_user.codsupervisor is None:
            raise HTTPException(
                status_code=403,
                detail="Supervisor sem CODSUPERVISOR configurado.",
            )

        return stmt.where(
            Vendedores.CODSUPERVISOR == current_user.codsupervisor
        )

    if role == "user":
        if current_user.codusur is None:
            raise HTTPException(
                status_code=403,
                detail="Usuário sem CODUSUR configurado.",
            )

        return stmt.where(
            Vendedores.CODUSUR == current_user.codusur
        )

    raise HTTPException(
        status_code=403,
        detail="Perfil sem escopo de acesso configurado.",
    )
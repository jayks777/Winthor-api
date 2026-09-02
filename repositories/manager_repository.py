from sqlalchemy.orm import Session
from db.uol_database import UolUser as User
from db.models import Supervisores
from core.settings import apply_max_results

class SupervisoresRepository:
    @staticmethod
    def get_all(db: Session, codsupervisor: int | None = None) -> list[Supervisores]:
        """Retorna todos os supervisores do sistema ordenados por CODSUPERVISOR."""
        query = db.query(Supervisores)
        if codsupervisor is not None:
            query = query.filter(Supervisores.CODSUPERVISOR == codsupervisor)
        query = query.order_by(Supervisores.CODSUPERVISOR)
        return apply_max_results(query).all()

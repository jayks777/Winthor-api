from sqlalchemy.orm import Session
from db.uol_database import UolUser as User
from db.models import Vendedores
from core.settings import apply_max_results

class UserRepository:
    @staticmethod
    def get_all(db: Session, codusur: int | None = None, codsupervisor: int | None = None) -> list[Vendedores]:
        """Retorna todos os vendedores do sistema ordenados por CODUSUR."""
        query = db.query(Vendedores)
        if codusur is not None:
            query = query.filter(Vendedores.CODUSUR == codusur)
        if codsupervisor is not None:
            query = query.filter(Vendedores.CODSUPERVISOR == codsupervisor)
        query = query.order_by(Vendedores.CODUSUR)
        return apply_max_results(query).all()
    
    @staticmethod
    def find_by_user(db: Session, usuario: str):
        return db.query(User).filter(User.usuario == usuario).first()
    
    @staticmethod
    def find_by_id(db: Session, id: int):
        return db.query(User).filter(User.id == id).first()
    
    @staticmethod
    def find_by_supervisor(db: Session, codsupervisor: int):
        return db.query(User).filter(User.codsupervisor == codsupervisor).first()
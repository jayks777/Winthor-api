from sqlalchemy.orm import Session
from db.uol_database import UolUser as User
from db.models import Vendedores

class UserRepository:
    @staticmethod
    def get_all(db: Session, limit: int = 100, codusur: int | None = None   , offset: int = 0) -> list[Vendedores]:
        """Retorna todos os vendedores do sistema ordenados por CODUSUR."""
        if codusur:
            return db.query(Vendedores).filter(Vendedores.CODUSUR == codusur).offset(offset).limit(limit).all()
        return db.query(Vendedores).order_by(Vendedores.CODUSUR).offset(offset).limit(limit).all()
    
    @staticmethod
    def find_by_user(db: Session, usuario: str):
        return db.query(User).filter(User.usuario == usuario).first()
    
    @staticmethod
    def find_by_id(db: Session, id: int):
        return db.query(User).filter(User.id == id).first()
    
    @staticmethod
    def create(db: Session, user: User):
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
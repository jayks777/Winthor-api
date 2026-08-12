from sqlalchemy.orm import Session
from db.uol_database import UolUser as User

class UserRepository:
    
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
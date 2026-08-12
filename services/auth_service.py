from sqlalchemy.orm import Session

from db.uol_database import UolUser as User
from core.encrypt import hash_password, verify_password
from repositories.user_repository import UserRepository

class AuthService:
    
    @staticmethod
    def create_user(db: Session, data):
        """Cria um novo usuário no banco de dados."""
        
        user_exists = UserRepository.find_by_user(db, data.usuario)
        
        if user_exists:
            return None

        hashed_password = hash_password(data.senha)
        user = User(
            usuario=data.usuario,
            email=getattr(data, "email", None),
            senha=hashed_password,
        )
        
        return UserRepository.create(db, user)

    @staticmethod
    def authenticate_user(db: Session, usuario: str, senha: str):
        
        user = UserRepository.find_by_user(db, usuario)
        
        if not user:
            return None
        
        if not verify_password(senha, user.senha):
            return None
        
        return user
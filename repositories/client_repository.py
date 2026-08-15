from sqlalchemy.orm import Session
from db.models import Clientes, Prestacoes

class ClientRepository:

    @staticmethod
    def find_all(db: Session, search: str | None = None, limit: int = 50, offset: int = 0):
        query = db.query(Clientes)
        if search:
            search_trimmed = search.strip()
            search_pattern = f"%{search_trimmed}%"
            if search_trimmed.isdigit():
                query = query.filter((Clientes.CODCLI == int(search_trimmed)) | (Clientes.CLIENTE.ilike(search_pattern)))
            else:
                query = query.filter(Clientes.CLIENTE.ilike(search_pattern))
        return query.order_by(Clientes.CODCLI).offset(offset).limit(limit).all()

    @staticmethod
    def find_by_id(db: Session, codcli: int):
        return db.query(Clientes).filter(Clientes.CODCLI == codcli).first()

    @staticmethod
    def find_prestacoes(db: Session, codcli: int):
        return db.query(Prestacoes).filter(Prestacoes.CODCLI == codcli).order_by(Prestacoes.DTVENC.desc()).all()


# class Clientes(Base):
#     __tablename__ = 'PCCLIENT'

#     CODCLI = Column(Integer, primary_key=True)
#     CLIENTE = Column(String(150))
#     RG = Column(String(20))   # CNPJ/CPF
#     ENDERENT = Column(String(100))  # Endereço de entrega
#     MUNICENT = Column(String(100))  # Município de entrega
#     TELENT = Column(String(30))   # Telefone de entrega
#     LIMCRED = Column(Numeric(15, 2))  # Limite de crédito
#     OBS = Column(String(255))   
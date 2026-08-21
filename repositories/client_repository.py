from sqlalchemy.orm import Session
from db.models import Clientes, Prestacoes
from core.settings import apply_max_results

class ClientRepository:

    @staticmethod
    def find_all(db: Session, search: str | None = None):
        query = db.query(Clientes)
        if search:
            search_trimmed = search.strip()
            search_pattern = f"%{search_trimmed}%"
            if search_trimmed.isdigit():
                query = query.filter((Clientes.CODCLI == int(search_trimmed)) | (Clientes.CLIENTE.ilike(search_pattern)))
            else:
                query = query.filter(Clientes.CLIENTE.ilike(search_pattern))
        query = query.order_by(Clientes.CODCLI)
        return apply_max_results(query).all()

    @staticmethod
    def find_by_id(db: Session, codcli: int):
        return db.query(Clientes).filter(Clientes.CODCLI == codcli).first()

    @staticmethod
    def find_prestacoes(
        db: Session,
        codcli: int,
    ):
        query = (
            db.query(Prestacoes)
            .filter(Prestacoes.CODCLI == codcli)
            .order_by(Prestacoes.DTVENC.desc(), Prestacoes.DUPLIC)
        )
        return apply_max_results(query).all()
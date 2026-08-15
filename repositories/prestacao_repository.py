from datetime import date, timedelta
from sqlalchemy.orm import Session
from db.models import Prestacoes

class PrestacaoRepository:

    @staticmethod
    def find_all(db: Session, codcli: int | None = None, codfilial: int | None = None, limit: int = 50, offset: int = 0):
        query = db.query(Prestacoes)
        if codcli is not None:
            query = query.filter(Prestacoes.CODCLI == codcli)
        if codfilial is not None:
            query = query.filter(Prestacoes.CODFILIAL == codfilial)
        return query.order_by(Prestacoes.DTVENC.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def find_vencidas(db: Session, codcli: int | None = None, limit: int = 50, offset: int = 0):
        today = date.today()
        query = db.query(Prestacoes).filter(
            Prestacoes.DTPAGTO.is_(None),
            Prestacoes.DTVENC < today
        )
        if codcli is not None:
            query = query.filter(Prestacoes.CODCLI == codcli)
        return query.order_by(Prestacoes.DTVENC.asc()).offset(offset).limit(limit).all()

    @staticmethod
    def find_a_vencer(db: Session, dias: int = 30, codcli: int | None = None, limit: int = 50, offset: int = 0):
        today = date.today()
        max_date = today + timedelta(days=dias)
        query = db.query(Prestacoes).filter(
            Prestacoes.DTPAGTO.is_(None),
            Prestacoes.DTVENC >= today,
            Prestacoes.DTVENC <= max_date
        )
        if codcli is not None:
            query = query.filter(Prestacoes.CODCLI == codcli)
        return query.order_by(Prestacoes.DTVENC.asc()).offset(offset).limit(limit).all()

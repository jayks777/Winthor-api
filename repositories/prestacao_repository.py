from datetime import date, timedelta

from sqlalchemy.orm import Session

from db.models import Clientes, Prestacoes
from db.uol_database import UolObservacoes


class PrestacaoRepository:
    @staticmethod
    def _base_query(db: Session):
        """Consulta explícita das prestações e do nome do cliente no WinThor."""
        return db.query(
            Prestacoes.DUPLIC,
            Prestacoes.CODCLI,
            Clientes.CLIENTE,
            Prestacoes.VALOR,
            Prestacoes.DTVENC,
            Prestacoes.DTEMISSAO,
            Prestacoes.DTBAIXA,
            Prestacoes.CODCOB,
            Prestacoes.CODFILIAL,
            Prestacoes.CODUSUR,
        ).outerjoin(Clientes, Clientes.CODCLI == Prestacoes.CODCLI)

    @staticmethod
    def serialize(rows, observacoes: dict[int, str] | None = None):
        observacoes = observacoes or {}
        return [
            {
                "DUPLIC": row.DUPLIC,
                "CODCLI": row.CODCLI,
                "CLIENTE": row.CLIENTE,
                "VALOR": float(row.VALOR) if row.VALOR is not None else None,
                "DTVENC": row.DTVENC,
                "DTEMISSAO": row.DTEMISSAO,
                "DTBAIXA": row.DTBAIXA,
                "CODCOB": row.CODCOB,
                "CODFILIAL": row.CODFILIAL,
                "CODUSUR": row.CODUSUR,
                "OBS": observacoes.get(row.DUPLIC),
            }
            for row in rows
        ]

    @staticmethod
    def observacoes_por_duplicata(db: Session, duplicatas: list[int]) -> dict[int, str]:
        if not duplicatas:
            return {}

        rows = db.query(UolObservacoes.duplic, UolObservacoes.obs).filter(
            UolObservacoes.duplic.in_(duplicatas)
        ).all()
        return {row.duplic: row.obs for row in rows}

    @staticmethod
    def find_all(
        db: Session,
        codcli: int | None = None,
        codfilial: int | None = None,
        dias_passados: int = 30,
        dias_futuros: int = 30,
        limit: int = 50,
        offset: int = 0,
    ):
        today = date.today()
        query = PrestacaoRepository._base_query(db).filter(
            Prestacoes.DTVENC >= today - timedelta(days=dias_passados),
            Prestacoes.DTVENC <= today + timedelta(days=dias_futuros),
        )
        if codcli is not None:
            query = query.filter(Prestacoes.CODCLI == codcli)
        if codfilial is not None:
            query = query.filter(Prestacoes.CODFILIAL == codfilial)
        return query.order_by(Prestacoes.DTVENC.desc(), Prestacoes.DUPLIC).offset(offset).limit(limit).all()

    @staticmethod
    def find_vencidas(
        db: Session,
        dias: int = 30,
        codcli: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        today = date.today()
        query = PrestacaoRepository._base_query(db).filter(
            Prestacoes.DTBAIXA.is_(None),
            Prestacoes.DTVENC >= today - timedelta(days=dias),
            Prestacoes.DTVENC < today,
        )
        if codcli is not None:
            query = query.filter(Prestacoes.CODCLI == codcli)
        return query.order_by(Prestacoes.DTVENC.asc(), Prestacoes.DUPLIC).offset(offset).limit(limit).all()

    @staticmethod
    def find_a_vencer(
        db: Session,
        dias: int = 30,
        codcli: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ):
        today = date.today()
        query = PrestacaoRepository._base_query(db).filter(
            Prestacoes.DTBAIXA.is_(None),
            Prestacoes.DTVENC >= today,
            Prestacoes.DTVENC <= today + timedelta(days=dias),
        )
        if codcli is not None:
            query = query.filter(Prestacoes.CODCLI == codcli)
        return query.order_by(Prestacoes.DTVENC.asc(), Prestacoes.DUPLIC).offset(offset).limit(limit).all()

    @staticmethod
    def find_by_duplic(db: Session, duplic: int):
        return PrestacaoRepository._base_query(db).filter(Prestacoes.DUPLIC == duplic).first()

    @staticmethod
    def upsert_observacao(db: Session, duplic: int, observacao: str) -> UolObservacoes:
        registro = db.query(UolObservacoes).filter(UolObservacoes.duplic == duplic).one_or_none()
        if registro is None:
            registro = UolObservacoes(duplic=duplic, obs=observacao)
            db.add(registro)
        else:
            registro.obs = observacao

        try:
            db.commit()
            db.refresh(registro)
        except Exception:
            db.rollback()
            raise
        return registro

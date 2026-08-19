from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import func
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
        codusur: int | None = None,
        limit: int = 50,
        offset: int = 0,
        search: str | None = None,
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
        if codusur is not None:
            query = query.filter(Prestacoes.CODUSUR == codusur)
        if search:
            term = f"%{search}%"
            query = query.filter(
                func.upper(Clientes.CLIENTE).like(func.upper(term))
                | func.to_char(Prestacoes.DUPLIC).like(term)
            )
        return query.order_by(Prestacoes.DTVENC.desc(), Prestacoes.DUPLIC).offset(offset).limit(limit).all()

    @staticmethod
    def find_a_vencer_por_dia(
        db: Session,
        dias: int = 30,
        codfilial: int | None = None,
    ) -> list[dict]:
        """Retorna total e quantidade de prestações a vencer agrupados por DTVENC.

        Preenche dias sem vencimentos com total=0 e quantidade=0.
        """
        today = date.today()
        end = today + timedelta(days=dias)

        query = (
            db.query(
                Prestacoes.DTVENC,
                func.sum(Prestacoes.VALOR).label("total"),
                func.count(Prestacoes.DUPLIC).label("quantidade"),
            )
            .filter(
                Prestacoes.DTBAIXA.is_(None),
                Prestacoes.DTVENC >= today,
                Prestacoes.DTVENC <= end,
            )
        )
        if codfilial is not None:
            query = query.filter(Prestacoes.CODFILIAL == codfilial)

        rows = query.group_by(Prestacoes.DTVENC).order_by(Prestacoes.DTVENC.asc()).all()

        # Indexar resultados por data
        by_date: dict[date, dict] = {
            row.DTVENC: {
                "DTVENC": row.DTVENC,
                "total": float(row.total) if row.total is not None else 0.0,
                "quantidade": row.quantidade,
            }
            for row in rows
        }

        # Gerar lista completa com zeros nos dias sem vencimento
        result = []
        for i in range(dias + 1):
            day = today + timedelta(days=i)
            result.append(
                by_date.get(
                    day,
                    {"DTVENC": day, "total": 0.0, "quantidade": 0},
                )
            )
        return result

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

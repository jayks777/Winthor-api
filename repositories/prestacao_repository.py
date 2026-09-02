from datetime import date, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from db.models import Clientes, Prestacoes
from db.uol_database import UolObservacoes
from core.cache import TTLCache
from core.settings import (
    OBS_IN_LIST_LIMIT,
    PRESTACOES_CACHE_TTL,
    apply_max_results,
)

_prestacoes_cache = TTLCache()


def _cached(label: str, key_params: tuple, fn):
    """Cacheia o resultado de uma query de prestações por TTL curto.

    O link com a base Oracle é o gargalo (latência + transferência por linha).
    As prestações mudam poucas vezes ao dia, então cachear o resultado por um
    TTL curto elimina a re-transferência de milhares de linhas em chamadas
    repetidas (ex.: dashboard).
    """
    key = (label, date.today().isoformat()) + tuple(key_params)
    cached = _prestacoes_cache.get(key)
    if cached is not None:
        return cached

    result = fn()
    _prestacoes_cache.set(key, result, PRESTACOES_CACHE_TTL)
    return result


class PrestacaoRepository:
    @staticmethod
    def _base_query(db: Session):
        """Consulta explícita das prestações e do nome do cliente no WinThor."""
        return db.query(
            Prestacoes.DUPLIC,
            Prestacoes.PREST,
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
    def _obs_key(row) -> tuple[int, str | None]:
        """Chave normalizada (duplic, prest) usada nos dicionários de observação."""
        prest = getattr(row, "PREST", None) if not isinstance(row, dict) else row.get("PREST")
        return (row.DUPLIC, str(prest) if prest is not None else None)

    @staticmethod
    def serialize(rows, observacoes: dict | None = None):
        observacoes = observacoes or {}
        return [
            {
                "DUPLIC": row.DUPLIC,
                "PREST": getattr(row, "PREST", None),
                "CODCLI": row.CODCLI,
                "CLIENTE": getattr(row, "CLIENTE", None),
                "VALOR": float(row.VALOR) if row.VALOR is not None else None,
                "DTVENC": row.DTVENC,
                "DTEMISSAO": row.DTEMISSAO,
                "DTBAIXA": row.DTBAIXA,
                "CODCOB": row.CODCOB,
                "CODFILIAL": row.CODFILIAL,
                "CODUSUR": row.CODUSUR,
                "OBS": observacoes.get(PrestacaoRepository._obs_key(row)),
            }
            for row in rows
        ]

    @staticmethod
    def observacoes_por_prestacoes(
        db: Session,
        duplicatas: list[int],
    ) -> dict[tuple[int, int | None], str]:
        if not duplicatas:
            return {}

        if len(duplicatas) <= OBS_IN_LIST_LIMIT:
            rows = db.query(
                UolObservacoes.duplic,
                UolObservacoes.prest,
                UolObservacoes.obs,
            ).filter(
                UolObservacoes.duplic.in_(duplicatas)
            ).all()
        else:
            # Lista grande (ex.: janela inteira com 13k duplicatas). Um
            # IN(...) com milhares de valores é lento para o MySQL gerar.
            # A tabela de observações é pequena (anotações manuais), então
            # trazê-la inteira e filtrar em Python é mais rápido.
            rows = db.query(
                UolObservacoes.duplic,
                UolObservacoes.prest,
                UolObservacoes.obs,
            ).all()

        duplic_set = set(duplicatas)

        # O PREST vem como varchar no WinThor, mas integer na base UOL.
        # Normaliza a chave para string para casar com a serialização.
        return {
            (row.duplic, str(row.prest) if row.prest is not None else None): row.obs
            for row in rows
            if row.duplic in duplic_set
        }

    @staticmethod
    def observacoes_por_duplicata(
        db: Session,
        duplicatas: list[int],
    ) -> dict[int, str]:
        if not duplicatas:
            return {}

        rows = db.query(
            UolObservacoes.duplic,
            UolObservacoes.obs,
        ).filter(
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
        venc: date | str | None = None,
        emissao: date | str | None = None,
        search: str | None = None,
        prest: str | None = None,
    ):
        def _run():
            nonlocal venc, emissao
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

            if prest is not None:
                query = query.filter(Prestacoes.PREST == prest)

            if search:
                term = search.strip()
                pattern = f"%{term}%"

                if term.isdigit():
                    query = query.filter(
                        (Prestacoes.DUPLIC == int(term))
                        | (
                            func.upper(Clientes.CLIENTE)
                            .like(func.upper(pattern))
                        )
                    )
                else:
                    query = query.filter(
                        func.upper(Clientes.CLIENTE)
                        .like(func.upper(pattern))
                    )

            # Garantir que a data seja realmente um date antes de enviar ao Oracle
            if venc:
                if isinstance(venc, str):
                    venc = date.fromisoformat(venc)

                query = query.filter(Prestacoes.DTVENC == venc)

            if emissao:
                if isinstance(emissao, str):
                    emissao = date.fromisoformat(emissao)

                query = query.filter(Prestacoes.DTEMISSAO == emissao)

            query = query.order_by(
                Prestacoes.DTVENC.desc(),
                Prestacoes.DUPLIC,
                Prestacoes.PREST,
            )

            return apply_max_results(query).all()

        return _cached(
            "find_all",
            (codcli, codfilial, dias_passados, dias_futuros, codusur, venc, emissao, search, prest),
            _run,
        )

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

        rows = (
            query
            .group_by(Prestacoes.DTVENC)
            .order_by(Prestacoes.DTVENC.asc())
            .all()
        )

        by_date: dict[date, dict] = {
            row.DTVENC: {
                "DTVENC": row.DTVENC,
                "total": float(row.total) if row.total is not None else 0.0,
                "quantidade": row.quantidade,
            }
            for row in rows
        }

        result = []

        for i in range(dias + 1):
            day = today + timedelta(days=i)

            result.append(
                by_date.get(
                    day,
                    {
                        "DTVENC": day,
                        "total": 0.0,
                        "quantidade": 0,
                    },
                )
            )

        return result

    @staticmethod
    def find_vencidas(
        db: Session,
        dias: int = 30,
        codcli: int | None = None,
    ):
        def _run():
            today = date.today()

            query = PrestacaoRepository._base_query(db).filter(
                Prestacoes.DTBAIXA.is_(None),
                Prestacoes.DTVENC >= today - timedelta(days=dias),
                Prestacoes.DTVENC < today,
            )

            if codcli is not None:
                query = query.filter(Prestacoes.CODCLI == codcli)

            query = query.order_by(
                Prestacoes.DTVENC.asc(),
                Prestacoes.DUPLIC,
                Prestacoes.PREST,
            )

            return apply_max_results(query).all()

        return _cached("find_vencidas", (dias, codcli), _run)

    @staticmethod
    def find_a_vencer(
        db: Session,
        dias: int = 30,
        codcli: int | None = None,
    ):
        def _run():
            today = date.today()

            query = PrestacaoRepository._base_query(db).filter(
                Prestacoes.DTBAIXA.is_(None),
                Prestacoes.DTVENC >= today,
                Prestacoes.DTVENC <= today + timedelta(days=dias),
            )

            if codcli is not None:
                query = query.filter(Prestacoes.CODCLI == codcli)

            query = query.order_by(
                Prestacoes.DTVENC.asc(),
                Prestacoes.DUPLIC,
                Prestacoes.PREST,
            )

            return apply_max_results(query).all()

        return _cached("find_a_vencer", (dias, codcli), _run)

    @staticmethod
    def find_by_duplic(db: Session, duplic: int, prest: str | None = None):
        query = (
            PrestacaoRepository
            ._base_query(db)
            .filter(Prestacoes.DUPLIC == duplic)
        )
        if prest is not None:
            query = query.filter(Prestacoes.PREST == prest)

        return query.first()

    @staticmethod
    def upsert_observacao(
        db: Session,
        duplic: int,
        prest: str | None,
        observacao: str,
    ) -> UolObservacoes:
        # O PREST é varchar no WinThor, mas integer na tabela UOL.
        prest_value = (
            int(prest)
            if prest is not None and str(prest).strip().isdigit()
            else None
        )

        registro = (
            db.query(UolObservacoes)
            .filter(
                UolObservacoes.duplic == duplic,
                UolObservacoes.prest == prest_value,
            )
            .one_or_none()
        )

        if registro is None:
            registro = UolObservacoes(
                duplic=duplic,
                prest=prest_value,
                obs=observacao,
            )
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
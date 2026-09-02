import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_MAX_RESULTS = int(os.getenv("API_MAX_RESULTS", "50000"))

# Cache das consultas de prestações (segundos). O link com o Oracle é lento;
# as prestações mudam poucas vezes ao dia, então um TTL curto evita
# re-transferir milhares de linhas a cada chamada.
PRESTACOES_CACHE_TTL = int(os.getenv("PRESTACOES_CACHE_TTL", "45"))

# Acima dessa quantidade de duplicatas, a busca de observações deixa de usar
# um IN(...) gigante e passa a trazer a tabela inteira (pequena) filtrando
# em Python.
OBS_IN_LIST_LIMIT = int(os.getenv("OBS_IN_LIST_LIMIT", "200"))


def apply_max_results(query):
    """Aplica o teto de segurança API_MAX_RESULTS a uma query SQLAlchemy."""
    if API_MAX_RESULTS and API_MAX_RESULTS > 0:
        query = query.limit(API_MAX_RESULTS)
    return query
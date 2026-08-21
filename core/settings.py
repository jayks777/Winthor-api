import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ------------------------------------------------------------------
# Teto de segurança (server-side) para os endpoints de listagem.
#
# Ao remover o parâmetro "limit" da API, os endpoints passam a
# retornar todos os registros, mas aplicamos este teto configurável
# no servidor para proteger o banco de consultas sem limite.
#
#   API_MAX_RESULTS = 0      -> sem limite (não recomendado)
#   API_MAX_RESULTS = 50000   -> retorna no máximo 50.000 registros
# ------------------------------------------------------------------
API_MAX_RESULTS = int(os.getenv("API_MAX_RESULTS", "50000"))


def apply_max_results(query):
    """Aplica o teto de segurança API_MAX_RESULTS a uma query SQLAlchemy."""
    if API_MAX_RESULTS and API_MAX_RESULTS > 0:
        query = query.limit(API_MAX_RESULTS)
    return query
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

API_MAX_RESULTS = int(os.getenv("API_MAX_RESULTS", "50000"))


def apply_max_results(query):
    """Aplica o teto de segurança API_MAX_RESULTS a uma query SQLAlchemy."""
    if API_MAX_RESULTS and API_MAX_RESULTS > 0:
        query = query.limit(API_MAX_RESULTS)
    return query
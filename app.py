from pathlib import Path
from fastapi import FastAPI
from config import configure_all

BASE_DIR = Path(__file__).resolve().parent

with open(BASE_DIR / "API.md", "r", encoding="utf-8") as f:
    description = f.read()

app = FastAPI(
    title="Winthor + iSA API | Riograndense",
    description=description
)

configure_all(app)
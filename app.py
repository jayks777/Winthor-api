from fastapi import FastAPI
from config import configure_all

with open("API.md", "r", encoding="utf-8") as f:
    description = f.read()

app = FastAPI(
    title="Winthor + iSA API",
    description=description
)

configure_all(app)

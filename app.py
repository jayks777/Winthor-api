from fastapi import FastAPI
from config import configure_all

app = FastAPI()

configure_all(app)

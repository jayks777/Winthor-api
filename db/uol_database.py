from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.engine import URL
import os

load_dotenv()


DATABASE_URL = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("UOL_USER"),
    password=os.getenv("UOL_PASSWORD"),
    host=os.getenv("UOL_HOST"),
    port=int(os.getenv("UOL_PORT", 3306)),
    database=os.getenv("UOL_NAME"),
)


engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

base = declarative_base()

class UolUser(base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True)
    usuario = Column(String(100))
    senha = Column(String(72))  
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint
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


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=40,
    pool_timeout=30,
)

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
    role = Column(String(50))

class UolObservacoes(base):
    __tablename__ = "prestacoes"
    __table_args__ = (UniqueConstraint("duplic", name="uq_prestacoes_duplic"),)

    id = Column(Integer, primary_key=True)
    duplic = Column(Integer, nullable=False)
    obs = Column(String(200))

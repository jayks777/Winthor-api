from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, UniqueConstraint, Boolean 
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
    codusur = Column(Integer, nullable=True)
    codsupervisor = Column(Integer, nullable=True)

class UolObservacoes(base):
    __tablename__ = "prestacoes"
    __table_args__ = (UniqueConstraint("duplic", "prest", name="uq_prestacoes_duplic_prest"),)

    id = Column(Integer, primary_key=True)
    duplic = Column(Integer, nullable=False)
    prest = Column(Integer, nullable=False)
    obs = Column(String(200))

class UolClientes(base):
    __tablename__ = "clientes"

    ID = Column(Integer, primary_key=True)
    CODCLI = Column(Integer, nullable=False, unique=True)
    NUMDOC = Column(String(14), nullable=False, unique=True)
    SENHA = Column(String(255), nullable=False)
    NOME = Column(String(100), nullable=False)
    PERMISSAO = Column(Boolean, nullable=False, default=False)
    CODUSUR = Column(Integer, nullable=True) #Vendedor responsável pelo cliente
    
class UolVendedores(base):
    __tablename__ = "vendedores"

    CODUSUR = Column(Integer, primary_key=True)
    NOME = Column(String(150))
    FOTO = Column(String(200), nullable=True) #caminho da foto do vendedor
    TELEFONE = Column(String(20), nullable=True) #telefone do vendedor
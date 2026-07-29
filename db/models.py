from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()

class Produtos(Base):
    __tablename__ = 'PCPRODUT'
    
    CODPROD = Column(Integer, primary_key=True)
    DESCRICAO = Column(String(150))
    EMBALAGEM = Column(String(100))
    UNIDADE = Column(String(3))
    CODSEC = Column(Integer)
    
class Categorias(Base):
    __tablename__ = 'PCSECAO'
    
    CODSEC = Column(Integer, primary_key=True)
    DESCRICAO = Column(String(150))
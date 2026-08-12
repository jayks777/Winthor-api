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
    CODEPTO = Column(Integer)
    
class Categorias(Base):
    __tablename__ = 'PCSECAO'
    
    CODSEC = Column(Integer, primary_key=True)
    DESCRICAO = Column(String(150))
    CODEPTO = Column(Integer)
    
class Departamentos(Base):
    __tablename__ = 'PCDEPTO'
    
    CODEPTO = Column(Integer, primary_key=True)
    DESCRICAO = Column(String(50))
    
class Estoque(Base):
    __tablename__ = 'PCEST'
    
    CODPROD = Column(Integer, primary_key=True, unique=False)
    CODFILIAL = Column(Integer)
    QTEST = Column(Integer)
    
class Clientes(Base):
    __tablename__ = 'PCCLIENT'
    
    CODCLI = Column(Integer, primary_key=True)
    CLIENTE = Column(String(150))
    MUNICCOB = Column(String(100))
    
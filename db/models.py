from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Numeric, Date
from sqlalchemy.types import Float

#tabelas do WinThor

Base = declarative_base()

class Produtos(Base):
    __tablename__ = 'PCPRODUT'
    
    CODPROD = Column(Integer, primary_key=True)
    DESCRICAO = Column(String(150))
    EMBALAGEM = Column(String(100))
    UNIDADE = Column(String(3))
    CODSEC = Column(Integer)
    PESOBRUTO = Column(Numeric(15, 3))
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
    CGCENT = Column(String(20))   # CNPJ/CPF
    ENDERENT = Column(String(100))  # Endereço de entrega
    MUNICENT = Column(String(100))  # Município de entrega
    TELENT = Column(String(30))   # Telefone de entrega
    LIMCRED = Column(Numeric(15, 2))  # Limite de crédito
    IEENT = Column(String(20)) # Inscrição Estadual de entrega
    OBS = Column(String(255))   


class Prestacoes(Base):
    __tablename__ = 'PCPREST'

    DUPLIC = Column(Integer, primary_key=True)  # Número da duplicata
    CODCLI = Column(Integer)
    VALOR = Column(Numeric(15, 2))
    DTVENC = Column(Date)         # Data de vencimento
    DTEMISSAO = Column(Date)         # Data de emissão
    DTBAIXA = Column(Date)         # Data de pagamento (NULL = em aberto)
    CODCOB = Column(String(10))   # Tipo de cobrança
    CODFILIAL = Column(Integer)
    CODUSUR = Column(Integer) #Código do vendedor

class Vendedores(Base):
    __tablename__ = 'PCUSUARI'

    CODUSUR = Column(Integer, primary_key=True)
    NOME = Column(String(150))
    CODSUPERVISOR = Column(Integer)

class Metas(Base):
    __tablename__ =  'PCMETARCA'

    CODUSUR = Column(Integer, primary_key=True)
    DATA = Column(Date)
    VLVENDAPREV = Column(Float)

class Pedidos(Base):
    __tablename__ = 'PCPEDC'

    NUMPED = Column(Integer, primary_key=True)
    CODCLI = Column(Integer)
    CODUSUR = Column(Integer)
    CODFILIAL = Column(Integer)
    CONDVENDA = Column(Integer)
    DATA = Column(Date)
    DTCANCEL = Column(Date)
    CODPRACA = Column(Integer)

class ItensPedido(Base):
    __tablename__ = 'PCPEDI'

    NUMPED = Column(Integer, primary_key=True)
    CODPROD = Column(Integer)
    QT = Column(Numeric(15, 3))
    PVENDA = Column(Numeric(15, 2))
    VLOUTRASDESP = Column(Numeric(15, 2))
    VLFRETE = Column(Numeric(15, 2))
    BONIFIC = Column(String(1))

class Supervisores(Base):
    __tablename__ = 'PCSUPERV'
    
    CODSUPERVISOR = Column(Integer, primary_key=True)
    NOME = Column(String(150))
from pydantic import BaseModel, Field

class ContactForm(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    empresa: str | None = Field(default=None, max_length=120)
    email: str
    mensagem: str = Field(min_length=10, max_length=4000)


class UserLogin(BaseModel):
    usuario: str
    senha: str


class UserResponse(BaseModel):
    id: int
    usuario: str
    role: str

    class Config:
        from_attributes = True


from datetime import date
from decimal import Decimal

class ClienteResponse(BaseModel):
    CODCLI: int
    CLIENTE: str | None = None
    CGCENT: str | None = None
    ENDERENT: str | None = None
    MUNICENT: str | None = None
    TELENT: str | None = None
    LIMCRED: Decimal | float | None = None
    IEENT: str | None = None
    OBS: str | None = None

    class Config:
        from_attributes = True


class PrestacaoResponse(BaseModel):
    DUPLIC: int
    CODCLI: int | None = None
    CLIENTE: str | None = None
    VALOR: Decimal | float | None = None
    DTVENC: date | None = None
    DTEMISSAO: date | None = None
    DTBAIXA: date | None = None
    CODCOB: str | None = None
    CODFILIAL: int | None = None
    CODUSUR: int | None = None #Código do vendedor
    OBS: str | None = None #Observação

    class Config:
        from_attributes = True


class PrestacaoObservacaoUpdate(BaseModel):
    observacao: str = Field(min_length=1, max_length=200)


class PrestacaoPorDiaResponse(BaseModel):
    DTVENC: date
    total: float
    quantidade: int


class ClienteComPrestacoes(ClienteResponse):
    prestacoes: list[PrestacaoResponse] = []

class UsuarioResponse(BaseModel):
    CODUSUR: int
    NOME: str | None = None

    class Config:
        from_attributes = True

class MetasResponse(BaseModel):
    CODUSUR: int
    DATA: date
    VLVENDAPREV: float

    class Config:
        from_attributes = True

class VendaPorVendedorResponse(BaseModel):
    CODUSUR: int
    NOME: str
    QTCLIPOS: int
    PVENDA: Decimal
    QT: Decimal
    TOTPESO: Decimal
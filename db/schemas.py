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
    email: str | None = None

    class Config:
        from_attributes = True
from pydantic import BaseModel, EmailStr, Field

class ContactForm(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    empresa: str | None = Field(default=None, max_length=120)
    email: EmailStr
    mensagem: str = Field(min_length=10, max_length=4000)

from fastapi import APIRouter, Request
from fastapi_mail import FastMail, MessageSchema, MessageType
from ..db.schemas import ContactForm
from ..config import configure_mail_channel
from ..utils.limiter import limiter

router = APIRouter(tags=['Comunicação'], prefix='/channel')

@router.post('/mail')
@limiter.limit("3/20minutes")
async def send_mail(request: Request, form: ContactForm):
    message = MessageSchema(
    subject="Novo contato pelo site",
    recipients=["contato@distribuidorariograndense.com.br"],
    body=f"""
Nome: {form.nome}

Empresa: {form.empresa}

Email: {form.email}

Mensagem:

{form.mensagem}
""",
    subtype=MessageType.plain,
    )

    fm = FastMail(configure_mail_channel())
    await fm.send_message(message)

    return {"success": True}


"""
Utilitário para gerar hash bcrypt de senhas.
Use para cadastrar usuários direto no banco de dados.

Uso:
    python tools/hash_password.py
"""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def main():
    print("=" * 50)
    print("  Gerador de Hash bcrypt")
    print("=" * 50)

    while True:
        senha = input("\nDigite a senha (ou 'sair' para encerrar): ").strip()

        if senha.lower() == "sair":
            print("Encerrando...")
            break

        if not senha:
            print("Senha nao pode ser vazia.")
            continue

        hashed = hash_password(senha)
        print(f"\nHash gerado:\n{hashed}")

        usuario = input("   Nome do usuario: ").strip()
        email   = input("   Email (Enter para pular): ").strip()
        email_val = f"'{email}'" if email else "NULL"
        print(
            f"\nINSERT INTO usuarios (usuario, email, senha)"
            f"\nVALUES ('{usuario}', {email_val}, '{hashed}');"
        )


if __name__ == "__main__":
    main()

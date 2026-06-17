"""Promove um usuário existente a Administrador.

Não há cadastro direto de admin (o /auth/registro só cria Cliente). O fluxo é:
1. registrar o usuário normalmente (UI /registro ou POST /auth/registro);
2. rodar este script com o e-mail dele.

Uso:
    cd backend
    venv\\Scripts\\python.exe scripts/promover_admin.py email@exemplo.com

Funciona com qualquer banco configurado em DATABASE_URL (usa o ORM da app).
"""
import os
import sys

from sqlalchemy import update

# Garante que o pacote `app` (em backend/) seja importável ao rodar de scripts/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models.usuario import Usuario


def promover(email: str) -> int:
    app = create_app()
    with app.app_context():
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario is None:
            print(f"[erro] usuario nao encontrado: {email}")
            return 1

        nome = usuario.nome
        # UPDATE direto na tabela: muda o discriminador STI sem mutar a
        # instancia ORM ja carregada (que ficaria inconsistente como Cliente).
        db.session.execute(
            update(Usuario)
            .where(Usuario.email == email)
            .values(tipo="admin", nivel_acesso=1)
        )
        db.session.commit()
        print(f"[ok] {nome} <{email}> promovido a admin (nivel_acesso=1)")
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python scripts/promover_admin.py <email>")
        raise SystemExit(2)
    raise SystemExit(promover(sys.argv[1]))

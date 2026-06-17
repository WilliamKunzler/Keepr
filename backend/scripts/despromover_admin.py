"""Rebaixa um Administrador de volta para Cliente.

Inverso de `promover_admin.py`: seta tipo='cliente' e limpa nivel_acesso.

Uso:
    cd backend
    venv\\Scripts\\python.exe scripts/despromover_admin.py email@exemplo.com

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


def despromover(email: str) -> int:
    app = create_app()
    with app.app_context():
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario is None:
            print(f"[erro] usuario nao encontrado: {email}")
            return 1
        if usuario.tipo != "admin":
            print(f"[info] {email} ja e cliente (tipo={usuario.tipo}); nada a fazer")
            return 0

        nome = usuario.nome
        # UPDATE direto: muda o discriminador STI e limpa a coluna de admin,
        # sem mutar a instancia ORM ja carregada (que ficaria inconsistente).
        db.session.execute(
            update(Usuario)
            .where(Usuario.email == email)
            .values(tipo="cliente", nivel_acesso=None)
        )
        db.session.commit()

        restantes = Usuario.query.filter_by(tipo="admin").count()
        print(f"[ok] {nome} <{email}> rebaixado para cliente")
        if restantes == 0:
            print("[aviso] nao ha mais nenhum administrador no sistema")
        else:
            print(f"[info] administradores restantes: {restantes}")
        return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("uso: python scripts/despromover_admin.py <email>")
        raise SystemExit(2)
    raise SystemExit(despromover(sys.argv[1]))

from functools import wraps

from flask import jsonify
from flask_jwt_extended import current_user, jwt_required


def admin_required(view):
    """Garante JWT válido E que o usuário é Administrador.

    Encadeia com `jwt_required` automaticamente — não precisa empilhar os dois
    decoradores na rota.
    """

    @wraps(view)
    @jwt_required()
    def wrapper(*args, **kwargs):
        if current_user is None or current_user.tipo != "admin":
            return jsonify({"erro": "acesso restrito a administradores"}), 403
        return view(*args, **kwargs)

    return wrapper

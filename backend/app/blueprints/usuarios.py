from flask import Blueprint, jsonify
from flask_jwt_extended import current_user

from app.blueprints._helpers import admin_required
from app.repositories.usuario_repo import UsuarioRepository
from app.services.events import event_bus

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.get("/")
@admin_required
def listar():
    usuarios = UsuarioRepository().get_all()
    return jsonify({"usuarios": [u.to_dict() for u in usuarios]})


@usuarios_bp.delete("/<int:usuario_id>")
@admin_required
def excluir(usuario_id: int):
    # Um administrador não pode remover a própria conta por esta tela.
    if usuario_id == current_user.id:
        return jsonify({"erro": "não é possível excluir o próprio usuário"}), 400

    repo = UsuarioRepository()
    usuario = repo.get(usuario_id)
    if usuario is None:
        return jsonify({"erro": "usuário não encontrado"}), 404

    repo.excluir_em_cascata(usuario)
    return "", 204


@usuarios_bp.post("/<int:usuario_id>/notificar-vencimentos")
@admin_required
def notificar_vencimentos(usuario_id: int):
    """Verifica produtos em risco de um usuário específico e dispara o Observer.

    Publica os mesmos eventos que os jobs diários, mas filtrado por usuário.
    InAppSubscriber e EmailSubscriber reagem normalmente — com deduplicação.
    """
    from app.models.produto import ProdutoValidade, ProdutoGarantia

    usuario = UsuarioRepository().get(usuario_id)
    if usuario is None:
        return jsonify({"erro": "usuário não encontrado"}), 404

    enviados = 0

    for produto in ProdutoValidade.query.filter_by(usuario_id=usuario_id).all():
        if produto.esta_em_risco(dias_antecedencia=7):
            event_bus.publish(
                "produto_vencendo",
                {"produto": produto, "dias": produto.dias_para_vencer()},
            )
            enviados += 1

    for produto in ProdutoGarantia.query.filter_by(usuario_id=usuario_id).all():
        if produto.esta_em_risco(dias_antecedencia=30):
            dias = produto.garantia.dias_restantes() if produto.garantia else None
            event_bus.publish("garantia_vencendo", {"produto": produto, "dias": dias})
            enviados += 1

    return jsonify({
        "ok": True,
        "usuario": usuario.nome,
        "produtos_em_risco": enviados,
    })

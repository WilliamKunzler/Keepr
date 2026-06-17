"""Blueprint notificações — exibe alertas in-app gerados pelo Observer."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user

from app.extensions import db
from app.models.notificacao import Notificacao

notificacoes_bp = Blueprint("notificacoes", __name__)


@notificacoes_bp.get("/")
@jwt_required()
def listar():
    notifs = (
        Notificacao.query
        .filter(
            Notificacao.usuario_id == current_user.id,
            ~Notificacao.tipo.like("email_%"),
        )
        .order_by(Notificacao.data_envio.desc())
        .all()
    )
    return jsonify({"notificacoes": [n.to_dict() for n in notifs]})


@notificacoes_bp.patch("/<int:notif_id>/lida")
@jwt_required()
def marcar_lida(notif_id: int):
    notif = Notificacao.query.filter_by(id=notif_id, usuario_id=current_user.id).first()
    if notif is None:
        return jsonify({"erro": "notificação não encontrada"}), 404
    notif.marcar_como_lida()
    db.session.commit()
    return jsonify({"notificacao": notif.to_dict()})


@notificacoes_bp.patch("/lida-todas")
@jwt_required()
def marcar_todas_lidas():
    Notificacao.query.filter_by(usuario_id=current_user.id, lida=False).update({"lida": True})
    db.session.commit()
    return jsonify({"ok": True})

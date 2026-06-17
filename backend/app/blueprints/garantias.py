"""Blueprint garantias — RF04 (consulta) e método consultarGarantias() do Cliente."""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, current_user

from app.repositories.garantia_repo import GarantiaRepository

garantias_bp = Blueprint("garantias", __name__)


@garantias_bp.get("/")
@jwt_required()
def listar():
    """Lista todas as garantias dos produtos do usuário autenticado."""
    garantias = GarantiaRepository().listar_por_usuario(current_user.id)
    return jsonify({"garantias": [g.to_dict() for g in garantias]})


@garantias_bp.get("/<int:garantia_id>")
@jwt_required()
def detalhe(garantia_id: int):
    repo = GarantiaRepository()
    garantia = repo.get(garantia_id)
    if garantia is None or garantia.produto.usuario_id != current_user.id:
        return jsonify({"erro": "garantia não encontrada"}), 404
    return jsonify({"garantia": garantia.to_dict()})

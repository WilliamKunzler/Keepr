from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user

from app.blueprints._helpers import admin_required
from app.repositories.relatorio_repo import RelatorioRepository
from app.schemas.relatorio import RelatorioCreate
from app.services.relatorio_service import RelatorioService

relatorios_bp = Blueprint("relatorios", __name__)


def _service() -> RelatorioService:
    return RelatorioService(repo=RelatorioRepository())


@relatorios_bp.get("/")
@admin_required
def listar():
    relatorios = RelatorioRepository().listar_por_administrador(current_user.id)
    return jsonify({"relatorios": [r.to_dict() for r in relatorios]})


@relatorios_bp.get("/<int:relatorio_id>")
@admin_required
def detalhe(relatorio_id: int):
    relatorio = RelatorioRepository().get(relatorio_id)
    if relatorio is None or relatorio.administrador_id != current_user.id:
        return jsonify({"erro": "relatório não encontrado"}), 404
    return jsonify({"relatorio": relatorio.to_dict()})


@relatorios_bp.post("/")
@admin_required
def gerar():
    dados = RelatorioCreate.model_validate(request.get_json() or {})
    relatorio = _service().gerar(dados.tipo, current_user.id)
    return jsonify({"relatorio": relatorio.to_dict()}), 201


@relatorios_bp.delete("/<int:relatorio_id>")
@admin_required
def excluir(relatorio_id: int):
    repo = RelatorioRepository()
    relatorio = repo.get(relatorio_id)
    if relatorio is None or relatorio.administrador_id != current_user.id:
        return jsonify({"erro": "relatório não encontrado"}), 404
    repo.delete(relatorio)
    return "", 204

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import current_user, jwt_required

from app.repositories.comprovante_repo import ComprovanteRepository
from app.schemas.comprovante import ConfirmarComprovante
from app.services.comprovante_service import ComprovanteService
from app.services.ocr_factory import get_ocr_service

comprovantes_bp = Blueprint("comprovantes", __name__)


def _service() -> ComprovanteService:
    return ComprovanteService(
        repo=ComprovanteRepository(),
        ocr=get_ocr_service(),
        upload_folder=current_app.config["UPLOAD_FOLDER"],
    )


@comprovantes_bp.post("/")
@jwt_required()
def upload():
    arquivo = request.files.get("arquivo")
    if arquivo is None or arquivo.filename == "":
        return jsonify({"erro": "campo 'arquivo' (multipart) é obrigatório"}), 400

    try:
        comprovante = _service().receber(
            nome_original=arquivo.filename,
            conteudo=arquivo.read(),
            usuario_id=current_user.id,
        )
    except ValueError as exc:
        return jsonify({"erro": str(exc)}), 422

    return jsonify({"comprovante": comprovante.to_dict()}), 201


@comprovantes_bp.get("/")
@jwt_required()
def listar():
    repo = ComprovanteRepository()
    comprovantes = repo.listar_por_usuario(current_user.id)
    return jsonify({"comprovantes": [c.to_dict() for c in comprovantes]})


@comprovantes_bp.get("/<int:comprovante_id>")
@jwt_required()
def detalhe(comprovante_id: int):
    comprovante = ComprovanteRepository().get_do_usuario(comprovante_id, current_user.id)
    if comprovante is None:
        return jsonify({"erro": "comprovante não encontrado"}), 404
    return jsonify({"comprovante": comprovante.to_dict()})


@comprovantes_bp.post("/<int:comprovante_id>/confirmar")
@jwt_required()
def confirmar(comprovante_id: int):
    service = _service()
    comprovante = service.repo.get_do_usuario(comprovante_id, current_user.id)
    if comprovante is None:
        return jsonify({"erro": "comprovante não encontrado"}), 404
    if comprovante.confirmado:
        return jsonify({"erro": "comprovante já confirmado"}), 409

    dados = ConfirmarComprovante.model_validate(request.get_json() or {})
    produtos = service.confirmar(comprovante, dados)
    return jsonify({
        "comprovante": comprovante.to_dict(),
        "produtos": [p.to_dict() for p in produtos],
    }), 201


@comprovantes_bp.delete("/<int:comprovante_id>")
@jwt_required()
def excluir(comprovante_id: int):
    service = _service()
    comprovante = service.repo.get_do_usuario(comprovante_id, current_user.id)
    if comprovante is None:
        return jsonify({"erro": "comprovante não encontrado"}), 404
    service.excluir(comprovante)
    return "", 204

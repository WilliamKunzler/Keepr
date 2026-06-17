from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, current_user

from app.repositories.produto_repo import ProdutoRepository
from app.schemas.produto import (
    ProdutoValidadeCreate,
    ProdutoGarantiaCreate,
    ProdutoUpdate,
)
from app.services.produto_service import ProdutoService

produtos_bp = Blueprint("produtos", __name__)


def _service() -> ProdutoService:
    return ProdutoService(repo=ProdutoRepository())


@produtos_bp.get("/")
@jwt_required()
def listar():
    svc = _service()
    termo = request.args.get("q", "").strip()
    if termo:
        produtos = svc.repo.buscar_por_nome(current_user.id, termo)
    else:
        produtos = svc.repo.listar_por_usuario(current_user.id)
    return jsonify({"produtos": [p.to_dict() for p in produtos]})


@produtos_bp.get("/vencendo")
@jwt_required()
def vencendo():
    dias = int(request.args.get("dias", 7))
    produtos = _service().repo.listar_validade_em_risco(current_user.id, dias)
    return jsonify({"produtos": [p.to_dict() for p in produtos], "dias": dias})


@produtos_bp.get("/garantia-vencendo")
@jwt_required()
def garantia_vencendo():
    dias = int(request.args.get("dias", 30))
    produtos = _service().repo.listar_garantia_em_risco(current_user.id, dias)
    return jsonify({"produtos": [p.to_dict() for p in produtos], "dias": dias})


@produtos_bp.get("/<int:produto_id>")
@jwt_required()
def detalhe(produto_id: int):
    produto = _service().repo.get_do_usuario(produto_id, current_user.id)
    if produto is None:
        return jsonify({"erro": "produto não encontrado"}), 404
    return jsonify({"produto": produto.to_dict()})


@produtos_bp.post("/")
@jwt_required()
def criar():
    body = request.get_json() or {}
    tipo = body.get("tipo")
    service = _service()

    if tipo == "validade":
        dados = ProdutoValidadeCreate.model_validate(body)
        produto = service.cadastrar_produto_validade(dados, current_user.id)
    elif tipo == "garantia":
        dados = ProdutoGarantiaCreate.model_validate(body)
        produto = service.cadastrar_produto_garantia(dados, current_user.id)
    else:
        return jsonify({"erro": "tipo deve ser 'validade' ou 'garantia'"}), 422

    return jsonify({"produto": produto.to_dict()}), 201


@produtos_bp.put("/<int:produto_id>")
@jwt_required()
def atualizar(produto_id: int):
    service = _service()
    produto = service.repo.get_do_usuario(produto_id, current_user.id)
    if produto is None:
        return jsonify({"erro": "produto não encontrado"}), 404

    dados = ProdutoUpdate.model_validate(request.get_json() or {})
    service.atualizar(produto, dados)
    return jsonify({"produto": produto.to_dict()})


@produtos_bp.delete("/<int:produto_id>")
@jwt_required()
def excluir(produto_id: int):
    service = _service()
    produto = service.repo.get_do_usuario(produto_id, current_user.id)
    if produto is None:
        return jsonify({"erro": "produto não encontrado"}), 404

    service.excluir(produto)
    return "", 204

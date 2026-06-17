"""Blueprint categorias — RF06.

Listagem: qualquer usuário autenticado.
Criação/edição/exclusão: somente Administrador (PDF: gerenciarCategorias).
"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.blueprints._helpers import admin_required
from app.repositories.categoria_repo import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate

categorias_bp = Blueprint("categorias", __name__)


@categorias_bp.get("/")
@jwt_required()
def listar():
    categorias = CategoriaRepository().get_all()
    return jsonify({"categorias": [c.to_dict() for c in categorias]})


@categorias_bp.post("/")
@admin_required
def criar():
    dados = CategoriaCreate.model_validate(request.get_json() or {})
    repo = CategoriaRepository()
    if repo.get_por_nome(dados.nome):
        return jsonify({"erro": "categoria já existe"}), 409

    from app.models.categoria import Categoria
    categoria = repo.save(Categoria(nome=dados.nome, descricao=dados.descricao))
    return jsonify({"categoria": categoria.to_dict()}), 201


@categorias_bp.put("/<int:categoria_id>")
@admin_required
def atualizar(categoria_id: int):
    repo = CategoriaRepository()
    categoria = repo.get(categoria_id)
    if categoria is None:
        return jsonify({"erro": "categoria não encontrada"}), 404

    dados = CategoriaUpdate.model_validate(request.get_json() or {})
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(categoria, campo, valor)
    repo.save(categoria)
    return jsonify({"categoria": categoria.to_dict()})


@categorias_bp.delete("/<int:categoria_id>")
@admin_required
def excluir(categoria_id: int):
    repo = CategoriaRepository()
    categoria = repo.get(categoria_id)
    if categoria is None:
        return jsonify({"erro": "categoria não encontrada"}), 404
    repo.delete(categoria)
    return "", 204

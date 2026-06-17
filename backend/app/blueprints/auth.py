from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    current_user,
    get_jwt_identity,
)

from app.extensions import db
from app.models.usuario import Cliente, Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/registro")
def registro():
    dados = request.get_json() or {}

    if not dados.get("email") or not dados.get("senha") or not dados.get("nome"):
        return jsonify({"erro": "nome, email e senha são obrigatórios"}), 400

    if Usuario.query.filter_by(email=dados["email"]).first():
        return jsonify({"erro": "email já cadastrado"}), 409

    cliente = Cliente(
        nome=dados["nome"],
        email=dados["email"],
        telefone=dados.get("telefone"),
    )
    cliente.set_senha(dados["senha"])

    db.session.add(cliente)
    db.session.commit()

    return jsonify({"usuario": cliente.to_dict()}), 201


@auth_bp.post("/login")
def login():
    dados = request.get_json() or {}

    usuario = Usuario.query.filter_by(email=dados.get("email", "")).first()
    if not usuario or not usuario.check_senha(dados.get("senha", "")):
        return jsonify({"erro": "credenciais inválidas"}), 401

    access = create_access_token(identity=usuario.id, additional_claims={"role": usuario.tipo})
    refresh = create_refresh_token(identity=usuario.id)

    return jsonify({
        "access_token": access,
        "refresh_token": refresh,
        "usuario": usuario.to_dict(),
    })


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    novo_access = create_access_token(identity=identity)
    return jsonify({"access_token": novo_access})


@auth_bp.get("/me")
@jwt_required()
def me():
    return jsonify({"usuario": current_user.to_dict()})

"""Blueprint home — health check e identificação da API."""
from flask import Blueprint, jsonify

home_bp = Blueprint("home", __name__)


@home_bp.get("/")
def index():
    return jsonify({
        "app": "Keepr",
        "version": "0.1.0",
        "tagline": "guarde notas, acompanhe garantias, nada vence esquecido",
        "status": "ok",
    })


@home_bp.get("/health")
def health():
    return jsonify({"status": "ok"})

import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pydantic import ValidationError

from .config import Config
from .extensions import db, jwt, scheduler


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(
        app,
        resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    _init_extensions(app)
    _register_error_handlers(app)
    _register_jwt_callbacks(app)
    _register_blueprints(app)
    _register_uploads_route(app)

    with app.app_context():
        _init_database()
        _init_observers()
        _init_scheduler()

    return app


def _init_extensions(app):
    db.init_app(app)
    jwt.init_app(app)
    scheduler.init_app(app)


def _register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        # include_context=False omite o objeto Exception original no `ctx`,
        # que o jsonify não sabe serializar.
        return jsonify({"erros": err.errors(include_context=False, include_url=False)}), 422

    @app.errorhandler(404)
    def handle_not_found(_err):
        return jsonify({"erro": "recurso não encontrado"}), 404

    @app.errorhandler(413)
    def handle_too_large(_err):
        return jsonify({"erro": "arquivo excede 10 MB"}), 413


def _register_jwt_callbacks(app):
    from .models.usuario import Usuario

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # Flask-JWT-Extended 4.7 exige `sub` como string (JWT RFC 7519 strict).
        raw = user.id if hasattr(user, "id") else user
        return str(raw)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(Usuario, int(identity))

    @jwt.expired_token_loader
    def expired_token_callback(_jwt_header, _jwt_payload):
        return jsonify({"erro": "token expirado"}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(_err):
        return jsonify({"erro": "token inválido"}), 401


def _register_blueprints(app):
    from .blueprints.home import home_bp
    from .blueprints.auth import auth_bp
    from .blueprints.produtos import produtos_bp
    from .blueprints.garantias import garantias_bp
    from .blueprints.categorias import categorias_bp
    from .blueprints.comprovantes import comprovantes_bp
    from .blueprints.notificacoes import notificacoes_bp
    from .blueprints.relatorios import relatorios_bp
    from .blueprints.usuarios import usuarios_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(produtos_bp, url_prefix="/produtos")
    app.register_blueprint(garantias_bp, url_prefix="/garantias")
    app.register_blueprint(categorias_bp, url_prefix="/categorias")
    app.register_blueprint(comprovantes_bp, url_prefix="/comprovantes")
    app.register_blueprint(notificacoes_bp, url_prefix="/notificacoes")
    app.register_blueprint(relatorios_bp, url_prefix="/relatorios")
    app.register_blueprint(usuarios_bp, url_prefix="/usuarios")


def _register_uploads_route(app):
    @app.route("/uploads/<path:filename>")
    def serve_upload(filename):
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


def _init_database():
    from . import models  # noqa: F401
    db.create_all()


def _init_observers():
    from .services.events import event_bus
    from .services.notificacao_service import EmailSubscriber, InAppSubscriber

    email = EmailSubscriber()
    in_app = InAppSubscriber()

    event_bus.subscribe("produto_vencendo", email)
    event_bus.subscribe("produto_vencendo", in_app)
    event_bus.subscribe("garantia_vencendo", email)
    event_bus.subscribe("garantia_vencendo", in_app)


def _init_scheduler():
    from .jobs.verificar_validade import verificar_validade
    from .jobs.verificar_garantia import verificar_garantia

    if scheduler.running:
        return

    scheduler.add_job(
        id="verificar_validade",
        func=verificar_validade,
        trigger="cron",
        hour=8,
        minute=0,
        replace_existing=True,
    )
    scheduler.add_job(
        id="verificar_garantia",
        func=verificar_garantia,
        trigger="cron",
        hour=8,
        minute=5,
        replace_existing=True,
    )
    scheduler.start()

import os
from datetime import timedelta

from flask import Flask, redirect, request, session, url_for
from werkzeug.security import generate_password_hash

from .models import Usuario, db


def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    instance_dir = os.path.join(basedir, "instance")
    os.makedirs(instance_dir, exist_ok=True)
    default_db_path = os.path.join(instance_dir, "gustavo.db")

    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-troque-em-producao")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", f"sqlite:///{default_db_path}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

    db.init_app(app)

    from .auth import auth_bp
    from .main import main_bp
    from .alunos import alunos_bp
    from .planos import planos_bp
    from .pagamentos import pagamentos_bp
    from .mensagens import mensagens_bp
    from .usuarios import usuarios_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(alunos_bp)
    app.register_blueprint(planos_bp)
    app.register_blueprint(pagamentos_bp)
    app.register_blueprint(mensagens_bp)
    app.register_blueprint(usuarios_bp)

    @app.before_request
    def exigir_login():
        endpoints_livres = {"auth.login", "static"}
        if not session.get("logado") and request.endpoint not in endpoints_livres:
            return redirect(url_for("auth.login"))

    with app.app_context():
        db.create_all()

        if Usuario.query.count() == 0:
            admin_user = os.environ.get("ADMIN_USER", "admin")
            admin_pass = os.environ.get("ADMIN_PASS", "academia123")
            db.session.add(
                Usuario(
                    nome="Administrador",
                    usuario=admin_user,
                    senha_hash=generate_password_hash(admin_pass),
                )
            )
            db.session.commit()

    return app

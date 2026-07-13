from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .models import Usuario

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        senha = request.form.get("senha", "")
        u = Usuario.query.filter_by(usuario=usuario).first()
        if u and check_password_hash(u.senha_hash, senha):
            session.permanent = True
            session["logado"] = True
            session["usuario_id"] = u.id
            session["usuario_nome"] = u.nome
            return redirect(url_for("main.dashboard"))
        flash("Usuário ou senha inválidos.")
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.security import generate_password_hash

from .models import Usuario, db

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/usuarios")


@usuarios_bp.route("/")
def listar():
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return render_template("usuarios/listar.html", usuarios=usuarios)


@usuarios_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        login = request.form["usuario"].strip()
        if Usuario.query.filter_by(usuario=login).first():
            flash("Já existe um usuário com esse login.")
            return render_template("usuarios/form.html", usuario=None)
        u = Usuario(
            nome=request.form["nome"],
            usuario=login,
            senha_hash=generate_password_hash(request.form["senha"]),
        )
        db.session.add(u)
        db.session.commit()
        flash("Usuário cadastrado com sucesso.")
        return redirect(url_for("usuarios.listar"))
    return render_template("usuarios/form.html", usuario=None)


@usuarios_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    u = Usuario.query.get_or_404(id)
    if request.method == "POST":
        u.nome = request.form["nome"]
        nova_senha = request.form.get("senha")
        if nova_senha:
            u.senha_hash = generate_password_hash(nova_senha)
        db.session.commit()
        flash("Usuário atualizado.")
        return redirect(url_for("usuarios.listar"))
    return render_template("usuarios/form.html", usuario=u)


@usuarios_bp.route("/<int:id>/excluir", methods=["POST"])
def excluir(id):
    if Usuario.query.count() <= 1:
        flash("Não é possível excluir o único usuário do sistema.")
        return redirect(url_for("usuarios.listar"))
    u = Usuario.query.get_or_404(id)
    db.session.delete(u)
    db.session.commit()
    flash("Usuário removido.")
    return redirect(url_for("usuarios.listar"))

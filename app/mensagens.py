from flask import Blueprint, flash, redirect, render_template, request, url_for

from .models import MensagemTemplate, db

mensagens_bp = Blueprint("mensagens", __name__, url_prefix="/mensagens")


@mensagens_bp.route("/")
def listar():
    templates = MensagemTemplate.query.order_by(MensagemTemplate.titulo).all()
    return render_template("mensagens/listar.html", templates=templates)


@mensagens_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        t = MensagemTemplate(titulo=request.form["titulo"], texto=request.form["texto"])
        db.session.add(t)
        db.session.commit()
        flash("Mensagem criada.")
        return redirect(url_for("mensagens.listar"))
    return render_template("mensagens/form.html", template=None)


@mensagens_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    t = MensagemTemplate.query.get_or_404(id)
    if request.method == "POST":
        t.titulo = request.form["titulo"]
        t.texto = request.form["texto"]
        db.session.commit()
        flash("Mensagem atualizada.")
        return redirect(url_for("mensagens.listar"))
    return render_template("mensagens/form.html", template=t)


@mensagens_bp.route("/<int:id>/excluir", methods=["POST"])
def excluir(id):
    t = MensagemTemplate.query.get_or_404(id)
    db.session.delete(t)
    db.session.commit()
    flash("Mensagem removida.")
    return redirect(url_for("mensagens.listar"))

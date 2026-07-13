from flask import Blueprint, flash, redirect, render_template, request, url_for

from .models import Plano, db

planos_bp = Blueprint("planos", __name__, url_prefix="/planos")


@planos_bp.route("/")
def listar():
    planos = Plano.query.order_by(Plano.nome).all()
    return render_template("planos/listar.html", planos=planos)


@planos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        plano = Plano(
            nome=request.form["nome"],
            valor=request.form["valor"].replace(",", "."),
            duracao_dias=request.form.get("duracao_dias") or 30,
        )
        db.session.add(plano)
        db.session.commit()
        flash("Plano cadastrado com sucesso.")
        return redirect(url_for("planos.listar"))
    return render_template("planos/form.html", plano=None)


@planos_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    plano = Plano.query.get_or_404(id)
    if request.method == "POST":
        plano.nome = request.form["nome"]
        plano.valor = request.form["valor"].replace(",", ".")
        plano.duracao_dias = request.form.get("duracao_dias") or 30
        db.session.commit()
        flash("Plano atualizado.")
        return redirect(url_for("planos.listar"))
    return render_template("planos/form.html", plano=plano)


@planos_bp.route("/<int:id>/excluir", methods=["POST"])
def excluir(id):
    plano = Plano.query.get_or_404(id)
    db.session.delete(plano)
    db.session.commit()
    flash("Plano removido.")
    return redirect(url_for("planos.listar"))

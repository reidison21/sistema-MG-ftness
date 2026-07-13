import re
from datetime import datetime
from urllib.parse import quote

from flask import Blueprint, flash, redirect, render_template, request, url_for

from .models import Aluno, MensagemTemplate, Plano, db

alunos_bp = Blueprint("alunos", __name__, url_prefix="/alunos")


def normalizar_telefone(numero):
    digitos = re.sub(r"\D", "", numero or "")
    if len(digitos) in (10, 11):
        digitos = "55" + digitos
    return digitos


@alunos_bp.route("/")
def listar():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    return render_template("alunos/listar.html", alunos=alunos)


@alunos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    planos = Plano.query.order_by(Plano.nome).all()
    if request.method == "POST":
        data_matricula_str = request.form.get("data_matricula")
        aluno = Aluno(
            nome=request.form["nome"],
            telefone=normalizar_telefone(request.form["telefone"]),
            email=request.form.get("email") or None,
            plano_id=request.form.get("plano_id") or None,
            data_matricula=(
                datetime.strptime(data_matricula_str, "%Y-%m-%d").date()
                if data_matricula_str
                else datetime.utcnow().date()
            ),
        )
        db.session.add(aluno)
        db.session.commit()
        flash("Aluno cadastrado com sucesso.")
        return redirect(url_for("alunos.listar"))
    return render_template("alunos/form.html", aluno=None, planos=planos)


@alunos_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    aluno = Aluno.query.get_or_404(id)
    planos = Plano.query.order_by(Plano.nome).all()
    if request.method == "POST":
        aluno.nome = request.form["nome"]
        aluno.telefone = normalizar_telefone(request.form["telefone"])
        aluno.email = request.form.get("email") or None
        aluno.plano_id = request.form.get("plano_id") or None
        aluno.ativo = bool(request.form.get("ativo"))
        db.session.commit()
        flash("Aluno atualizado.")
        return redirect(url_for("alunos.listar"))
    return render_template("alunos/form.html", aluno=aluno, planos=planos)


@alunos_bp.route("/<int:id>/excluir", methods=["POST"])
def excluir(id):
    aluno = Aluno.query.get_or_404(id)
    db.session.delete(aluno)
    db.session.commit()
    flash("Aluno removido.")
    return redirect(url_for("alunos.listar"))


@alunos_bp.route("/<int:id>/mensagens")
def mensagens(id):
    aluno = Aluno.query.get_or_404(id)
    templates = MensagemTemplate.query.order_by(MensagemTemplate.titulo).all()
    links = []
    for t in templates:
        texto = t.texto.replace("{nome}", aluno.nome)
        link = f"https://wa.me/{aluno.telefone}?text={quote(texto)}"
        links.append({"titulo": t.titulo, "texto": texto, "link": link})
    return render_template("alunos/mensagens.html", aluno=aluno, links=links)

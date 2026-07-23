import csv
import io
import re
from datetime import datetime, timedelta
from urllib.parse import quote

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for

from .models import Aluno, MensagemTemplate, Pagamento, Plano, db
from .utils import status_vencimento

alunos_bp = Blueprint("alunos", __name__, url_prefix="/alunos")


def normalizar_telefone(numero):
    digitos = re.sub(r"\D", "", numero or "")
    if len(digitos) in (10, 11):
        digitos = "55" + digitos
    return digitos


@alunos_bp.route("/")
def listar():
    q = request.args.get("q", "").strip()
    consulta = Aluno.query
    if q:
        consulta = consulta.filter(Aluno.nome.ilike(f"%{q}%"))
    alunos = consulta.order_by(Aluno.nome).all()
    vencimentos = {aluno.id: status_vencimento(aluno) for aluno in alunos}
    return render_template("alunos/listar.html", alunos=alunos, q=q, vencimentos=vencimentos)


@alunos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    planos = Plano.query.order_by(Plano.nome).all()
    if request.method == "POST":
        data_matricula_str = request.form.get("data_matricula")
        data_matricula = (
            datetime.strptime(data_matricula_str, "%Y-%m-%d").date()
            if data_matricula_str
            else datetime.utcnow().date()
        )
        plano_id = request.form.get("plano_id") or None
        plano = Plano.query.get(plano_id) if plano_id else None

        vencimento_str = request.form.get("vencimento")
        if vencimento_str:
            vencimento = datetime.strptime(vencimento_str, "%Y-%m-%d").date()
        elif plano:
            vencimento = data_matricula + timedelta(days=plano.duracao_dias)
        else:
            vencimento = None

        aluno = Aluno(
            nome=request.form["nome"],
            telefone=normalizar_telefone(request.form["telefone"]),
            email=request.form.get("email") or None,
            plano_id=plano_id,
            data_matricula=data_matricula,
            vencimento=vencimento,
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
        vencimento_str = request.form.get("vencimento")
        aluno.vencimento = (
            datetime.strptime(vencimento_str, "%Y-%m-%d").date() if vencimento_str else None
        )
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


@alunos_bp.route("/vencidos")
def vencidos():
    filtro = request.args.get("status", "pendentes")

    alunos_ativos = Aluno.query.filter_by(ativo=True).order_by(Aluno.nome).all()
    itens = [(aluno, status_vencimento(aluno)) for aluno in alunos_ativos]

    if filtro == "pendentes":
        itens = [i for i in itens if i[1]["status"] in ("vencido", "vencendo")]
    elif filtro in ("vencido", "vencendo", "em_dia", "sem_plano"):
        itens = [i for i in itens if i[1]["status"] == filtro]
    # filtro == "todos" -> mantém todos os alunos ativos

    itens.sort(key=lambda item: item[1]["dias"] if item[1]["dias"] is not None else 99999)
    return render_template("alunos/vencidos.html", itens=itens, filtro=filtro)


@alunos_bp.route("/<int:id>")
def detalhe(id):
    aluno = Aluno.query.get_or_404(id)
    pagamentos = (
        Pagamento.query.filter_by(aluno_id=aluno.id)
        .order_by(Pagamento.mes_referencia.desc())
        .all()
    )
    vencimento = status_vencimento(aluno)
    return render_template(
        "alunos/detalhe.html", aluno=aluno, pagamentos=pagamentos, vencimento=vencimento
    )


@alunos_bp.route("/<int:id>/mensagens")
def mensagens(id):
    aluno = Aluno.query.get_or_404(id)
    templates = MensagemTemplate.query.order_by(MensagemTemplate.titulo).all()
    vencimento = status_vencimento(aluno)
    vencimento_str = (
        vencimento["data_vencimento"].strftime("%d/%m/%Y")
        if vencimento["data_vencimento"]
        else "não definido"
    )
    links = []
    for t in templates:
        texto = (
            t.texto.replace("{nome}", aluno.nome)
            .replace("{vencimento}", vencimento_str)
            .replace("{data}", vencimento_str)
            .replace("{data_vencimento}", vencimento_str)
        )
        link = f"https://wa.me/{aluno.telefone}?text={quote(texto)}"
        links.append({"titulo": t.titulo, "texto": texto, "link": link})
    return render_template("alunos/mensagens.html", aluno=aluno, links=links)


@alunos_bp.route("/buscar.json")
def buscar_json():
    q = request.args.get("q", "").strip()
    if not q:
        return jsonify([])
    alunos = (
        Aluno.query.filter(Aluno.nome.ilike(f"%{q}%"))
        .order_by(Aluno.nome)
        .limit(8)
        .all()
    )
    resultado = []
    for aluno in alunos:
        info = status_vencimento(aluno)
        resultado.append(
            {
                "id": aluno.id,
                "nome": aluno.nome,
                "plano": aluno.plano.nome if aluno.plano else None,
                "status": info["status"],
                "ativo": aluno.ativo,
            }
        )
    return jsonify(resultado)


@alunos_bp.route("/exportar.csv")
def exportar_csv():
    alunos = Aluno.query.order_by(Aluno.nome).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["Nome", "Telefone", "Email", "Plano", "Data matrícula", "Status", "Vencimento"]
    )
    for aluno in alunos:
        info = status_vencimento(aluno)
        writer.writerow(
            [
                aluno.nome,
                aluno.telefone,
                aluno.email or "",
                aluno.plano.nome if aluno.plano else "",
                aluno.data_matricula.isoformat(),
                "Ativo" if aluno.ativo else "Inativo",
                info["data_vencimento"].isoformat() if info["data_vencimento"] else "",
            ]
        )
    csv_data = "﻿" + output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=alunos.csv"},
    )

import csv
import io
from datetime import date, datetime, timedelta

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from .models import Aluno, Pagamento, db

pagamentos_bp = Blueprint("pagamentos", __name__, url_prefix="/pagamentos")


@pagamentos_bp.route("/")
def listar():
    mes = request.args.get("mes") or date.today().strftime("%Y-%m")

    alunos_ativos = Aluno.query.filter_by(ativo=True).all()
    for aluno in alunos_ativos:
        existe = Pagamento.query.filter_by(aluno_id=aluno.id, mes_referencia=mes).first()
        if not existe:
            db.session.add(Pagamento(aluno_id=aluno.id, mes_referencia=mes, status="pendente"))
    db.session.commit()

    registros = (
        Pagamento.query.join(Aluno)
        .filter(Pagamento.mes_referencia == mes)
        .order_by(Aluno.nome)
        .all()
    )
    total_mes = sum(r.valor or 0 for r in registros if r.status == "pago")
    return render_template("pagamentos/listar.html", registros=registros, mes=mes, total_mes=total_mes)


@pagamentos_bp.route("/<int:id>/alternar", methods=["POST"])
def alternar(id):
    pagamento = Pagamento.query.get_or_404(id)
    if pagamento.status == "pago":
        pagamento.status = "pendente"
        pagamento.data_pagamento = None
        pagamento.valor = None
    else:
        pagamento.status = "pago"
        pagamento.data_pagamento = date.today()
        pagamento.valor = pagamento.aluno.plano.valor if pagamento.aluno.plano else 0
        if pagamento.aluno.plano:
            pagamento.aluno.vencimento = date.today() + timedelta(
                days=pagamento.aluno.plano.duracao_dias
            )
    db.session.commit()
    return redirect(url_for("pagamentos.listar", mes=pagamento.mes_referencia))


@pagamentos_bp.route("/renovar/<int:aluno_id>", methods=["POST"])
def renovar(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    data_str = request.form.get("data")
    if data_str:
        data_pagamento = datetime.strptime(data_str, "%Y-%m-%d").date()
    else:
        data_pagamento = date.today()

    mes = data_pagamento.strftime("%Y-%m")
    pagamento = Pagamento.query.filter_by(aluno_id=aluno.id, mes_referencia=mes).first()
    if not pagamento:
        pagamento = Pagamento(aluno_id=aluno.id, mes_referencia=mes)
        db.session.add(pagamento)
    pagamento.status = "pago"
    pagamento.data_pagamento = data_pagamento
    pagamento.valor = aluno.plano.valor if aluno.plano else 0
    if aluno.plano:
        aluno.vencimento = data_pagamento + timedelta(days=aluno.plano.duracao_dias)
    db.session.commit()
    flash(f"Pagamento de {aluno.nome} renovado a partir de {data_pagamento.strftime('%d/%m/%Y')}.")
    return redirect(request.referrer or url_for("alunos.vencidos"))


@pagamentos_bp.route("/historico")
def historico():
    resultados = (
        db.session.query(
            Pagamento.mes_referencia,
            func.coalesce(func.sum(Pagamento.valor), 0).label("total"),
            func.count(Pagamento.id).label("qtd_pagos"),
        )
        .filter(Pagamento.status == "pago")
        .group_by(Pagamento.mes_referencia)
        .order_by(Pagamento.mes_referencia.desc())
        .all()
    )
    return render_template("pagamentos/historico.html", resultados=resultados)


@pagamentos_bp.route("/historico.csv")
def historico_csv():
    resultados = (
        db.session.query(
            Pagamento.mes_referencia,
            func.coalesce(func.sum(Pagamento.valor), 0).label("total"),
            func.count(Pagamento.id).label("qtd_pagos"),
        )
        .filter(Pagamento.status == "pago")
        .group_by(Pagamento.mes_referencia)
        .order_by(Pagamento.mes_referencia.desc())
        .all()
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Mês", "Alunos pagos", "Total recebido"])
    for mes_referencia, total, qtd_pagos in resultados:
        writer.writerow([mes_referencia, qtd_pagos, f"{total:.2f}"])
    csv_data = "﻿" + output.getvalue()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=historico_recebimentos.csv"},
    )

from datetime import date

from flask import Blueprint, redirect, render_template, request, url_for

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
    return render_template("pagamentos/listar.html", registros=registros, mes=mes)


@pagamentos_bp.route("/<int:id>/alternar", methods=["POST"])
def alternar(id):
    pagamento = Pagamento.query.get_or_404(id)
    if pagamento.status == "pago":
        pagamento.status = "pendente"
        pagamento.data_pagamento = None
    else:
        pagamento.status = "pago"
        pagamento.data_pagamento = date.today()
    db.session.commit()
    return redirect(url_for("pagamentos.listar", mes=pagamento.mes_referencia))

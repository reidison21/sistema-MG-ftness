from datetime import date

from flask import Blueprint, render_template
from sqlalchemy import func

from .models import Aluno, Pagamento, db
from .utils import status_vencimento

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    mes_atual = date.today().strftime("%Y-%m")
    alunos_ativos = Aluno.query.filter_by(ativo=True).all()
    total_alunos = len(alunos_ativos)
    pagos = Pagamento.query.filter_by(mes_referencia=mes_atual, status="pago").count()
    pendentes = Pagamento.query.filter_by(mes_referencia=mes_atual, status="pendente").count()
    total_recebido = (
        db.session.query(func.coalesce(func.sum(Pagamento.valor), 0))
        .filter(Pagamento.mes_referencia == mes_atual, Pagamento.status == "pago")
        .scalar()
    )

    alertas = []
    for aluno in alunos_ativos:
        info = status_vencimento(aluno)
        if info["status"] in ("vencido", "vencendo"):
            alertas.append((aluno, info))
    alertas.sort(key=lambda item: item[1]["dias"])

    return render_template(
        "dashboard.html",
        total_alunos=total_alunos,
        pagos=pagos,
        pendentes=pendentes,
        total_recebido=total_recebido,
        mes_atual=mes_atual,
        alertas=alertas,
    )

from datetime import date

from flask import Blueprint, render_template
from sqlalchemy import func

from .models import Aluno, Pagamento, db

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    mes_atual = date.today().strftime("%Y-%m")
    total_alunos = Aluno.query.filter_by(ativo=True).count()
    pagos = Pagamento.query.filter_by(mes_referencia=mes_atual, status="pago").count()
    pendentes = Pagamento.query.filter_by(mes_referencia=mes_atual, status="pendente").count()
    total_recebido = (
        db.session.query(func.coalesce(func.sum(Pagamento.valor), 0))
        .filter(Pagamento.mes_referencia == mes_atual, Pagamento.status == "pago")
        .scalar()
    )
    return render_template(
        "dashboard.html",
        total_alunos=total_alunos,
        pagos=pagos,
        pendentes=pendentes,
        total_recebido=total_recebido,
        mes_atual=mes_atual,
    )

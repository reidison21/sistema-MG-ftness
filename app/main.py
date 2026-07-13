from datetime import date

from flask import Blueprint, render_template

from .models import Aluno, Pagamento

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    mes_atual = date.today().strftime("%Y-%m")
    total_alunos = Aluno.query.filter_by(ativo=True).count()
    pagos = Pagamento.query.filter_by(mes_referencia=mes_atual, status="pago").count()
    pendentes = Pagamento.query.filter_by(mes_referencia=mes_atual, status="pendente").count()
    return render_template(
        "dashboard.html",
        total_alunos=total_alunos,
        pagos=pagos,
        pendentes=pendentes,
        mes_atual=mes_atual,
    )

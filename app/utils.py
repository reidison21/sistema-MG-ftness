from datetime import date, timedelta

from .models import Pagamento


def status_vencimento(aluno):
    if not aluno.plano:
        return {"status": "sem_plano", "data_vencimento": None, "dias": None}

    ultimo_pago = (
        Pagamento.query.filter_by(aluno_id=aluno.id, status="pago")
        .filter(Pagamento.data_pagamento.isnot(None))
        .order_by(Pagamento.data_pagamento.desc())
        .first()
    )
    base = ultimo_pago.data_pagamento if ultimo_pago else aluno.data_matricula
    data_vencimento = base + timedelta(days=aluno.plano.duracao_dias)
    dias = (data_vencimento - date.today()).days

    if dias < 0:
        status = "vencido"
    elif dias <= 5:
        status = "vencendo"
    else:
        status = "em_dia"

    return {"status": status, "data_vencimento": data_vencimento, "dias": dias}

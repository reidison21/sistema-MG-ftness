from datetime import date


def status_vencimento(aluno):
    if not aluno.vencimento:
        return {"status": "sem_plano", "data_vencimento": None, "dias": None}

    dias = (aluno.vencimento - date.today()).days

    if dias < 0:
        status = "vencido"
    elif dias <= 5:
        status = "vencendo"
    else:
        status = "em_dia"

    return {"status": status, "data_vencimento": aluno.vencimento, "dias": dias}

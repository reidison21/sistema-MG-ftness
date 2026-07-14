from datetime import date

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Plano(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    duracao_dias = db.Column(db.Integer, nullable=False, default=30)

    alunos = db.relationship("Aluno", backref="plano", lazy=True)


class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(150))
    plano_id = db.Column(db.Integer, db.ForeignKey("plano.id"))
    data_matricula = db.Column(db.Date, nullable=False, default=date.today)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    vencimento = db.Column(db.Date)

    pagamentos = db.relationship(
        "Pagamento", backref="aluno", lazy=True, cascade="all, delete-orphan"
    )


class Pagamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey("aluno.id"), nullable=False)
    mes_referencia = db.Column(db.String(7), nullable=False)  # formato YYYY-MM
    status = db.Column(db.String(10), nullable=False, default="pendente")  # pago | pendente
    data_pagamento = db.Column(db.Date)
    valor = db.Column(db.Numeric(10, 2))


class MensagemTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)


class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    usuario = db.Column(db.String(80), nullable=False, unique=True)
    senha_hash = db.Column(db.String(255), nullable=False)

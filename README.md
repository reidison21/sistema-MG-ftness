# MG Fitness - Gestão de Academia

Sistema simples para cadastrar alunos e planos, controlar pagamentos mensais e
enviar mensagens padrão para os alunos via WhatsApp (usando links `wa.me`,
sem precisar de API paga do WhatsApp).

## Como rodar localmente

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

Acesse http://127.0.0.1:5000 no navegador.

Na primeira execução o sistema cria automaticamente um usuário administrador:
- usuário: `admin`
- senha: `academia123`

Depois de entrar, vá em **Usuários** no menu para trocar a senha, criar
outros usuários (ex: um para cada pessoa da academia) ou remover o admin
padrão (não é possível excluir o único usuário existente).

O banco de dados SQLite é criado automaticamente em `instance/gustavo.db`
na primeira execução.

## Configuração (opcional)

Copie `.env.example` para `.env` e ajuste `SECRET_KEY` (chave de segurança
da sessão) e `ADMIN_USER`/`ADMIN_PASS` (só valem para o usuário criado
automaticamente na primeira vez que o sistema roda, antes de existir
qualquer usuário no banco). Para que essas variáveis sejam carregadas
automaticamente, instale `python-dotenv` (já está no `requirements.txt`)
e adicione no topo do `run.py`:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Como funciona o envio de WhatsApp

Cadastre uma ou mais "Mensagens padrão" (menu Mensagens). Na lista de
Alunos, clique em "WhatsApp" ao lado do aluno desejado — o sistema mostra
as mensagens já com o nome do aluno preenchido e um botão que abre o
WhatsApp Web/App com o número e o texto prontos para envio. Você ainda
precisa clicar em enviar dentro do WhatsApp (isso é proposital: evita
bloqueios por automação e não exige nenhuma conta de desenvolvedor).

## Deploy (colocar no ar com seu domínio)

Ver recomendação completa em conversa anterior: Render.com (app) +
Supabase (Postgres gratuito) é a combinação mais simples e gratuita.
Nesse caso, basta definir a variável de ambiente `DATABASE_URL` com a
string de conexão do Supabase que o sistema passa a usar Postgres em vez
de SQLite automaticamente.

# FinderBit Estoque MVP

MVP de um micro SaaS de controle de estoque com Django, renderizacao server-side, HTMX e Tailwind via CDN.

## Stack

- Python 3.13
- Django
- SQLite
- Django Templates
- HTMX
- Tailwind CSS

## Estrutura

- `config`: configuracao central do projeto
- `accounts`: empresa, perfil do usuario, login e contexto da empresa
- `dashboard`: indicadores iniciais do painel
- `inventory`: produtos, movimentacoes, estoque atual, historico e seed

## Regras implementadas

- saldo de estoque calculado apenas a partir das movimentacoes
- entrada soma quantidade
- saida subtrai quantidade
- saida com saldo negativo e bloqueada na validacao do model
- todo produto e movimentacao pertence a uma empresa
- todo usuario autenticado opera dentro da empresa vinculada em `UserProfile`
- listagens e operacoes filtradas pela empresa do usuario autenticado

## Funcionalidades da Sprint 1

- categorias estruturadas por empresa
- busca, filtros e ordenacao em produtos
- busca, filtros e ordenacao em estoque atual
- filtros e ordenacao no historico
- exportacao CSV de produtos, estoque atual e movimentacoes
- dashboard com periodo de analise e metricas operacionais

## Como rodar

1. Crie e ative um ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

3. Execute as migracoes:

```bash
python manage.py migrate
```

4. Opcional: carregar dados de exemplo:

```bash
python manage.py seed_mvp
```

5. Inicie o servidor:

```bash
python manage.py runserver
```

6. Acesse:

- app: `http://127.0.0.1:8000/accounts/login/`
- admin: `http://127.0.0.1:8000/admin/`

## Usuario demo

Ao rodar `seed_mvp`:

- usuario: `demo`
- senha: `demo1234`

## Admin

Para criar um superusuario:

```bash
python manage.py createsuperuser
```

No admin, associe usuarios a empresas criando ou editando `UserProfile`.

## Deploy na Vercel (Django)

O projeto agora esta configurado para deploy na Vercel com runtime Python via `api/index.py` e `vercel.json`.
Nao usamos a chave `builds` no `vercel.json`, para que as configuracoes de Build/Install do projeto na Vercel continuem valendo.

### 1) Variaveis de ambiente recomendadas

Configure no painel da Vercel:

- `DJANGO_SECRET_KEY`: chave secreta forte para producao.
- `DJANGO_DEBUG`: `False` em producao.
- `DJANGO_ALLOWED_HOSTS`: por exemplo `.vercel.app,seu-dominio.com`.
- `DJANGO_CSRF_TRUSTED_ORIGINS`: por exemplo `https://seu-projeto.vercel.app,https://seu-dominio.com`.
- `DATABASE_URL`: URL de banco Postgres (Neon, Supabase, etc).

### 2) Banco de dados

Em producao, use Postgres via `DATABASE_URL`. O SQLite local nao e recomendado para Vercel.
Sem `DATABASE_URL`, o app cai em SQLite temporario em `/tmp/db.sqlite3` (ephemero), util apenas para teste rapido.

### 3) Comandos uteis antes do deploy

```bash
python manage.py check --deploy
python manage.py migrate
```

### 4) Observacao sobre migracoes

Em Vercel, migracoes nao rodam automaticamente. Execute `python manage.py migrate` conectado ao mesmo banco de producao sempre que houver novas migracoes.

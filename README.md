# FinderBit Estoque

Sistema de gestão de estoque com Django, Bootstrap 5 e HTMX SPA.

![Django](https://img.shields.io/badge/Django-5.1+-092E2?style=flat&logo=django)
![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=flat&logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5-7952B3?style=flat&logo=bootstrap)
![HTMX](https://img.shields.io/badge/HTMX-OK-blue?style=flat)

## ✨ Funcionalidades

- 📦 Cadastro de produtos com múltiplas unidades (UN, MT, LT, KG, FL, PC)
- 🔄 Movimentações de entrada/saída com controle de estoque
- 🎨 Design System Ruby Red com Light/Dark Mode
- ⚡ Interface SPA com HTMX (sem page reload)
- 📱 Responsivo (Mobile-friendly)
- 🔗 Banco de dados MySQL/PostgreSQL/SQLite

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# 1. Clonar e entrar no diretório
cd estoque-django

# 2. Criar ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Criar arquivo .env
cp .env.example.dev .env

# 5. Executar migrações
python manage.py migrate

# 6. Criar superusuário
python manage.py createsuperuser

# 7. Executar servidor
python manage.py runserver
```

Acesse: http://localhost:8000

---

## 🐳 Docker

### Desenvolvimento

```bash
cp .env.example.dev .env
docker compose -f docker-compose.yml up --build
```

### Produção

```bash
cp .env.example.prod .env
docker compose -f docker-compose.yml up --build -d
```

---

## 📋 Variáveis de Ambiente

### `.env.prod` (Produção)

| Variável | Descrição | Exemplo |
|---------|----------|---------|
| `DJANGO_SECRET_KEY` | Chave secreta do Django | `gere-em-djec.in/secret/` |
| `DJANGO_DEBUG` | Modo debug | `False` |
| `ALLOWED_HOSTS` | Domínios permitidos | `estoque.com.br` |
| `DOMAIN` | Domínio principal | `https://estoque.com.br` |
| `CSRF_TRUSTED_ORIGINS` | Origens CSRF | `https://estoque.com.br` |
| `MYSQL_HOST` | Host do MySQL | `estoquefb.mysql.uhserver.com` |
| `MYSQL_PORT` | Porta do MySQL | `3306` |
| `MYSQL_NAME` | Nome do banco | `estoquefb` |
| `MYSQL_USER` | Usuário do MySQL | `mateus1` |
| `MYSQL_PASSWORD` | Senha do MySQL | `***` |
| `HOST` | Host do servidor | `0.0.0.0` |
| `HOST_PORT` | Porta do servidor | `8000` |

### `.env.dev` (Desenvolvimento)

| Variável | Descrição | Exemplo |
|----------|----------|---------|
| `DJANGO_DEBUG` | Modo debug | `True` |
| `ALLOWED_HOSTS` | Domínios permitidos | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | Origens CSRF | `http://localhost:8000` |
| `MYSQL_HOST` | (opcional) | `localhost` |

---

## 🎯 Unidades de Medida

O sistema suporta materiais de confecção e estamparia:

| Código | Descrição | Uso típico |
|--------|----------|-----------|
| `UN` | Unidade | Peças avulsas |
| `MT` | Metros | Tecidos, fitas |
| `LT` | Litros | Tintas, solventes |
| `KG` | Quilos | Aviamentos |
| `FL` | Folhas | Papel, papelão |
| `PC` | Peças | Zíper, botão |

---

## 📁 Estrutura

```
estoque-django/
├── accounts/          # Autenticação
├── core/             # Template tags
├── dashboard/        # Dashboard
├── inventory/        # Estoque
├── templates/        # Templates HTML
├── static/           # CSS, JS, imagens
├── config/           # Configurações Django
├── Dockerfile       # Container Docker
├── docker-compose.yml
├── requirements.txt
└── manage.py
```

---

## 🔧 Comandos Úteis

```bash
# Migrações
python manage.py makemigrations
python manage.py migrate

# Coletar static
python manage.py collectstatic --noinput

# Criar superusuário
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Testar conexão com banco
python manage.py dbshell
```

---

## 🔐 Segurança (Produção)

- ✅ `DJANGO_DEBUG=False`
- ✅ `SESSION_COOKIE_SECURE=True`
- ✅ `CSRF_COOKIE_SECURE=True`
- ✅ Altere `DJANGO_SECRET_KEY`
- ✅ Use HTTPS
- ✅ Configure firewall (libere só a porta 80/443)

---

## 📄 Licença

MIT © FinderBit
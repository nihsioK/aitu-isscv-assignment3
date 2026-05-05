# AI-Assisted Telecom Billing MVP

Практическая работа №6, задание 2. Вариант 6: телекоммуникации, регистрация клиентов и выставление счетов.

Это отдельная AI-assisted версия MVP. Она реализует тот же бизнес-сценарий, что и версия задания 1, но код и структура подготовлены как самостоятельное решение с использованием AI-assistance.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- JWT через `python-jose`
- bcrypt
- Static HTML/CSS/JS frontend
- Docker Compose
- ruff, mypy, bandit, pip-audit

## Business Scenario

Клиент регистрируется, входит в систему, смотрит тарифы, активирует тариф и просматривает свои счета. Администратор создает invoice за расчетный месяц, но операция требует admin JWT и внутренний заголовок `X-Internal-Billing-Key`.

## API

- `GET /` - web UI.
- `POST /auth/register` - регистрация клиента.
- `POST /auth/login` - получение JWT.
- `GET /auth/me` - профиль текущего пользователя.
- `GET /plans` - публичные тарифы.
- `POST /plans/activate` - активация тарифа.
- `GET /billing/invoices` - счета текущего пользователя.
- `GET /billing/invoices/{invoice_id}` - invoice с object-level authorization.
- `POST /billing/generate` - генерация invoice админом и внутренним ключом.

## Local Run

```bash
cp .env.example .env
# replace all replace_with_* values
make sync
make run
```

UI: `http://localhost:8000/`

## Docker Run

```bash
cp .env.example .env
# replace all replace_with_* values
make docker-up
```

UI in Docker: `http://localhost:8001/`

## Checks

```bash
make lint
make typecheck
make security
make audit
make smoke
make check
```

## Security Mechanisms

- Strong password validation.
- Password hashing with bcrypt.
- JWT with expiration.
- RBAC for admin invoice generation.
- Object-level authorization for invoice details.
- Internal billing key for sensitive billing operation.
- Request body size limit.
- Redis-based failed login limit.
- Backend-calculated invoice amount.
- Duplicate invoice prevention per customer and month.
- Security logs without passwords, tokens, email or request bodies.
- Generic 500 handler without traceback leakage.

## Assignment 2 Documents

- `AI_USAGE.md` - concrete AI tools and prompts.
- `SECURITY_ANALYSIS.md` - OWASP Top 10 analysis.
- `COMPARISON.md` - comparison with Assignment 1 version.
- `main.tex` - final report source.

# P6: Telecom Billing MVP

Практическая работа №6, вариант 6: телекоммуникации, регистрация клиентов и выставление счетов.

MVP представляет собой небольшую billing-систему: клиент регистрируется, входит в систему, выбирает тариф и просматривает свои счета. Администратор вместе с внутренним billing-ключом может создать invoice за расчетный период.

## Стек

- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- JWT через `python-jose`
- bcrypt для паролей
- Docker Compose
- ruff, bandit, pip-audit, mypy для проверок

Основные слои:

- `app/api/routes`: HTTP endpoint-ы и UI.
- `app/schemas`: Pydantic-схемы и входная валидация.
- `app/services`: бизнес-логика регистрации, тарифов и биллинга.
- `app/repositories`: запросы к базе данных через SQLAlchemy.
- `app/models`: ORM-модели.
- `app/core`: конфигурация, безопасность, логи, обработка ошибок.

## Сущности БД

- `users`: клиенты и администраторы.
- `tariffs`: тарифные планы.
- `invoices`: счета клиентов.

При первом запуске seed создает более 200 строк данных: admin, demo client, 100 дополнительных клиентов, 5 тарифов и счета по нескольким периодам.

## Роли и доступ

| Действие | Public | Client | Admin | Admin + Internal API Key |
|---|---:|---:|---:|---:|
| Регистрация | Да | Да | Да | Да |
| Login | Да | Да | Да | Да |
| Просмотр тарифов | Да | Да | Да | Да |
| Активация тарифа | Нет | Только себе | Да | Да |
| Генерация счета | Нет | Нет | Нет | Да |
| Просмотр своих счетов | Нет | Да | Да | Да |
| Просмотр чужого invoice | Нет | 404 | Да | Да |

## API

- `GET /`: минимальный UI.
- `POST /auth/register`: регистрация клиента.
- `POST /auth/login`: выдача JWT.
- `GET /tariffs`: список активных тарифов.
- `POST /tariffs/activate`: подключение тарифа текущему пользователю.
- `POST /billing/generate-invoice`: создание invoice админом с `X-Internal-API-Key`.
- `GET /billing/my-invoices`: счета текущего пользователя.
- `GET /billing/invoices/{invoice_id}`: просмотр invoice с object-level authorization.

## Настройка

```bash
uv sync
cp .env.example .env
```

В `.env` нужно заменить значения:

- `POSTGRES_PASSWORD`
- `DATABASE_URL`
- `SECRET_KEY`
- `INTERNAL_API_KEY`
- `ADMIN_INITIAL_PASSWORD`
- `DEMO_CLIENT_PASSWORD`

`SECRET_KEY` должен быть не короче 32 символов, `INTERNAL_API_KEY` не короче 24 символов. Оба значения не должны оставаться примерными.

## Запуск локально

```bash
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

UI доступен на `http://localhost:8000/`.

API docs доступны на `http://localhost:8000/docs`.

## Запуск через Docker

```bash
docker compose up --build
```

PostgreSQL и Redis поднимаются вместе с API. Пароль базы берется из `.env`, а не хранится в `docker-compose.yml`.

## Реализованные механизмы безопасности

- bcrypt-хеширование паролей.
- JWT access token с истечением срока действия.
- Проверка силы `SECRET_KEY` и `INTERNAL_API_KEY` на старте.
- Pydantic validation и запрет лишних полей в чувствительных request body.
- RBAC для admin endpoint-ов.
- Object-level authorization для invoice.
- Возврат 404 для чужого invoice, чтобы не раскрывать факт существования счета.
- Rate limit неуспешных login-попыток через Redis.
- Middleware ограничения размера request body.
- Расчет суммы invoice только на backend-е по активному тарифу.
- Защита от повторного счета за один период.
- Security logging без паролей, токенов, email и полного body.
- Общий exception handler без утечки traceback в response.
- Dependency audit через `pip-audit`.

## OWASP Top 10 Analysis

| OWASP риск | Где проверено | Что сделано |
|---|---|---|
| Broken Access Control | `/billing/invoices/{id}`, `/billing/generate-invoice` | RBAC, internal key, проверка владельца invoice |
| Security Misconfiguration | `.env`, `docker-compose.yml`, `Dockerfile` | секреты вынесены в env, убран reload в Docker, слабые ключи запрещены |
| Software Supply Chain Failures | `pyproject.toml`, `uv.lock` | удалены лишние test/dev зависимости, используется `pip-audit` |
| Cryptographic Failures | `app/core/security.py`, `app/core/config.py` | bcrypt, JWT secret validation, plain password не сохраняется |
| Injection | repositories | SQLAlchemy query API, нет ручной SQL-конкатенации |
| Insecure Design | billing flow | сумма и тариф счета рассчитываются на сервере |
| Authentication Failures | login service | bcrypt, JWT exp, Redis login failure limit |
| Software or Data Integrity Failures | invoice generation | запрет дублей по `user_id + billing_period`, backend-calculated amount |
| Security Logging and Alerting Failures | services/dependencies | события логируются по ID без чувствительных данных |
| Mishandling of Exceptional Conditions | `app/core/exceptions.py` | наружу возвращается общий 500 без деталей ошибки |

## Таблица уязвимостей и исправлений

| Риск | Место | Описание | Последствия | Критичность | Исправление |
|---|---|---|---|---|---|
| Небезопасная конфигурация | `app/core/config.py`, `.env.example` | слабый JWT/internal key мог остаться из примера | подделка token или вызов billing API | High | строгая валидация env на старте |
| Broken Access Control | `/billing/generate-invoice` | одного admin JWT недостаточно для внутренней операции | создание финансовых документов при компрометации admin token | High | добавлен `X-Internal-API-Key` |
| Insecure Design | `/billing/generate-invoice` | сумма счета могла контролироваться входным JSON в старой версии | неправильные финансовые данные | High | amount/tariff/currency рассчитываются backend-ом |
| Data Integrity Failure | invoice generation | можно было повторить счет за период в старой версии | двойное начисление | Medium | проверка существующего invoice за период |
| Information Disclosure | `/billing/invoices/{id}` | разные ответы для чужого и отсутствующего invoice | клиент узнает факт существования чужого счета | Medium | для чужого invoice возвращается 404 |
| Resource Consumption | все JSON endpoint-ы | большой request body доходил до обработки | лишний расход ресурсов | Medium | middleware возвращает 413 до route handler-а |
| Logging Failure | auth/billing logs | риск записи ПДн или token в logs | утечка чувствительных данных | Medium | логируются только event name и технические ID |
| Supply Chain Risk | dependencies | лишние test/dev пакеты увеличивали поверхность | больше стороннего кода и audit шума | Low | зависимости очищены, lockfile обновлен |

## Повторная проверка

Команды для финальной проверки:

```bash
uv run ruff check app
uv run bandit -r app
uv run pip-audit
uv run mypy app
```

Ручные проверки:

- регистрация клиента возвращает `201`;
- login возвращает JWT;
- слабый пароль отклоняется Pydantic validation;
- клиент может активировать тариф только себе;
- invoice создается по активному тарифу клиента;
- повторный invoice за период возвращает `409`;
- генерация invoice без internal key возвращает `403`;
- чужой invoice для клиента возвращает `404`;
- слишком большой request body возвращает `413`.

## Вывод

После доработки MVP закрывает требования задания 1: есть UI, больше пяти API endpoint-ов, три сущности БД, две роли, 200+ seed rows, реализованный billing-сценарий, валидация, хеширование паролей, разграничение доступа, security logging, Docker Compose и анализ по OWASP Top 10.

# Telecom Billing MVP — Assignment 3, Variant 6

Subscriber registration and billing system built with FastAPI + SQLAlchemy + SQLite.

## Setup

### Prerequisites
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) package manager

### 1. Install dependencies

```bash
uv sync
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set SECRET_KEY to a long random string
```

### 3. Run the application

```bash
uv run uvicorn app.main:app --reload
```

API docs available at: http://localhost:8000/docs

## Project structure

```
app/
├── main.py              — FastAPI application entry point
├── core/
│   ├── config.py        — Settings loaded from .env
│   ├── security.py      — Password hashing and JWT utilities
│   ├── logging.py       — Logging configuration
│   └── exceptions.py    — Global exception handlers
├── db/
│   ├── base.py          — SQLAlchemy declarative base
│   ├── session.py       — DB engine and session factory
│   └── init_db.py       — Table creation and seed data
├── models/              — SQLAlchemy ORM models
├── schemas/             — Pydantic request/response schemas
├── repositories/        — Database access layer
├── services/            — Business logic layer
├── api/routes/          — HTTP route handlers
├── dependencies/        — FastAPI dependency injection (auth, roles)
└── tests/               — Test suite
```

## Development tools

```bash
# Static analysis
uv run bandit -r app

# Dependency vulnerability scan
uv run pip-audit

# Tests
uv run pytest
```

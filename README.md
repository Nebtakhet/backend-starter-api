# Backend Starter API

<p align="center">
	<strong>FastAPI starter project with a clean, modular structure, SQLAlchemy models, Alembic migrations, and JWT auth.</strong>
</p>

<p align="center">
	<a href="https://www.python.org/">
		<img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue">
	</a>
	<a href="https://fastapi.tiangolo.com/">
		<img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.100%2B-009688">
	</a>
	<a href="https://www.sqlalchemy.org/">
		<img alt="SQLAlchemy" src="https://img.shields.io/badge/SQLAlchemy-2.0%2B-d71f00">
	</a>
	<a href="https://docs.astral.sh/ruff/">
		<img alt="Ruff" src="https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json">
	</a>
	<a href="https://github.com/Nebtakhet/backend-starter-api/actions/workflows/ci.yml">
		<img alt="CI" src="https://github.com/Nebtakhet/backend-starter-api/actions/workflows/ci.yml/badge.svg">
	</a>
	<a href="https://github.com/pre-commit/pre-commit">
		<img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen">
	</a>
</p>

<p align="center">
	<a href="#-quick-start">Quick start</a>
	·
	<a href="#-installation">Installation</a>
	·
	<a href="#-configuration">Configuration</a>
	·
	<a href="#-api-endpoints-summary">Endpoints</a>
	·
	<a href="#-tests">Tests</a>
	·
	<a href="#-quality-checks">Quality checks</a>
	·
	<a href="#-docker">Docker</a>
</p>

## ✨ Features

- FastAPI app scaffolded for growth
- SQLAlchemy models + Alembic migrations
- JWT auth with refresh tokens (hashed in DB)
- Refresh token rotation + reuse detection (revokes all tokens)
- Access token validation with iss/aud/iat + clock skew
- Rate limiting on auth endpoints
- Modular services, schemas, and API routers
- Items CRUD with ownership enforcement
- /users/me endpoint
- Health endpoint
- Test suite with pytest

## ⚡ At a glance

| Layer | What’s included |
| --- | --- |
| Auth | Login, refresh, logout, hashed refresh tokens |
| Users | Register, list, me |
| Items | Full CRUD + ownership checks |
| Ops | Health, Docker Compose, test coverage |

## 🧭 Project structure

```text
backend-starter-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   ├── db/
│   ├── schemas/
│   ├── api/
│   ├── services/
│   └── utils/
├── tests/
├── alembic/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── README.md
└── LICENSE
```

## 🚀 Quick start

1) Create a .env file based on .env.example.
2) Install dependencies: pip install -e ".[dev]"
3) Run the API: uvicorn app.main:app --reload
4) Open docs: http://localhost:8000/docs

## 📦 Installation

Requirements:
- Python 3.11+
- (Optional) PostgreSQL
- (Optional) Docker + Docker Compose

Create a virtual environment and install dependencies:

python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

Start the API locally:

uvicorn app.main:app --reload

## ⚙️ Configuration

Set the environment variables in your .env file. Use .env.example as the template.

Required:
- PROJECT_NAME
- SECRET_KEY
- REFRESH_TOKEN_SECRET
- JWT_ISSUER
- JWT_AUDIENCE
- CLOCK_SKEW_SECONDS
- ACCESS_TOKEN_EXPIRE_MINUTES
- AUTH_LOGIN_RATE_LIMIT
- AUTH_REFRESH_RATE_LIMIT
- SQLALCHEMY_DATABASE_URI

Optional:
- REFRESH_TOKEN_EXPIRE_DAYS

Notes:
- Default DB is SQLite unless SQLALCHEMY_DATABASE_URI is set.
- Docker Compose uses Postgres and expects SQLALCHEMY_DATABASE_URI in .env.

## 🧱 Migrations

- Create a migration: alembic revision --autogenerate -m "init"
- Apply migrations: alembic upgrade head

## 🐳 Docker

docker compose up --build

## ✅ Tests

pytest

## ✅ Quality checks

Run Ruff and mypy locally:

ruff check .
ruff format .
mypy app tests

Docker:

docker compose run --rm --no-deps -e SQLALCHEMY_DATABASE_URI=sqlite:///./test.db api sh -c "pip install -e .[dev] && python -m pytest"

Note: `python -m pytest` avoids PATH issues when dev tools are installed to the user site inside the container.
Note: Tests default to SQLite via environment overrides in [tests/conftest.py](tests/conftest.py).

## 🔐 Auth flow (summary)

1) Register a user
2) Login to receive access + refresh tokens
3) Use access token for protected endpoints
4) Refresh to rotate refresh token
5) Logout to revoke refresh token

## 📚 API endpoints (summary)

Auth:
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout

Users:
- POST /api/v1/users
- GET /api/v1/users
- GET /api/v1/users/me

Items (auth required):
- POST /api/v1/items
- GET /api/v1/items
- GET /api/v1/items/{item_id}
- PUT /api/v1/items/{item_id}
- DELETE /api/v1/items/{item_id}

Health:
- GET /health

## 🧪 Error format

All errors follow a consistent shape:

{ "detail": "...", "code": "...", "errors": [...] }

Notes:
- Validation errors use code validation_error and include errors.
- Auth/authorization errors use code auth_error.
- DB integrity errors use code db_integrity_error.

## 🧩 API versioning

All routes are mounted under /api/v1 by default.

## 📄 License

See LICENSE
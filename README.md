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
	<a href="https://github.com/psf/black">
		<img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000">
	</a>
	<a href="https://github.com/pre-commit/pre-commit">
		<img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen">
	</a>
</p>

<p align="center">
	<a href="#quick-start-local">Quick start</a>
	·
	<a href="#api-endpoints-summary">Endpoints</a>
	·
	<a href="#tests">Tests</a>
	·
	<a href="#docker">Docker</a>
</p>

## Features

- FastAPI app scaffolded for growth
- SQLAlchemy models + Alembic migrations
- JWT auth with refresh tokens (hashed in DB)
- Modular services, schemas, and API routers
- Items CRUD with ownership enforcement
- /users/me endpoint
- Health endpoint
- Test suite with pytest

## At a glance

| Layer | What’s included |
| --- | --- |
| Auth | Login, refresh, logout, hashed refresh tokens |
| Users | Register, list, me |
| Items | Full CRUD + ownership checks |
| Ops | Health, Docker Compose, test coverage |

## Project structure

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

## Quick start (local)

1) Create a .env file based on .env.example.
2) Install dependencies: pip install -e .[dev]
3) Run the API: uvicorn app.main:app --reload
4) Open docs: http://localhost:8000/docs

## Configuration

Set the environment variables in your .env file. Use .env.example as the template.

Required:
- PROJECT_NAME
- SECRET_KEY
- ACCESS_TOKEN_EXPIRE_MINUTES
- SQLALCHEMY_DATABASE_URI

Optional:
- REFRESH_TOKEN_EXPIRE_DAYS

## Migrations

- Create a migration: alembic revision --autogenerate -m "init"
- Apply migrations: alembic upgrade head

## Docker

docker compose up --build

## Tests

pytest

Docker:

docker compose run --rm -e SQLALCHEMY_DATABASE_URI=sqlite:///./test.db api sh -c "pip install -e .[dev] && pytest"

## API endpoints (summary)

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

## API versioning

All routes are mounted under /api/v1 by default.

## License

See LICENSE
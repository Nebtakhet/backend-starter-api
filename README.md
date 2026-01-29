# Backend Starter API

<p align="center">
	<strong>FastAPI starter project with a clean, modular structure, SQLAlchemy models, Alembic migrations, and basic auth endpoints.</strong>
</p>

<p align="center">
	<a href="https://www.python.org/">
		<img alt="Python" src="https://img.shields.io/badge/python-3.10%2B-blue">
	</a>
	<a href="https://fastapi.tiangolo.com/">
		<img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.100%2B-009688">
	</a>
	<a href="https://github.com/psf/black">
		<img alt="Black" src="https://img.shields.io/badge/code%20style-black-000000">
	</a>
	<a href="https://github.com/pre-commit/pre-commit">
		<img alt="pre-commit" src="https://img.shields.io/badge/pre--commit-enabled-brightgreen">
	</a>
</p>

## Features

- FastAPI app scaffolded for growth
- SQLAlchemy models + Alembic migrations
- JWT-based auth flow (signup/login)
- Modular services, schemas, and API routers
- Test suite with pytest

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

## Migrations

- Create a migration: alembic revision --autogenerate -m "init"
- Apply migrations: alembic upgrade head

## Docker

docker compose up --build

## Tests

pytest

## API versioning

All routes are mounted under /api/v1 by default.

## License

See LICENSE.
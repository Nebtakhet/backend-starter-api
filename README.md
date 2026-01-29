# Backend Starter API

FastAPI starter project with modular structure, SQLAlchemy models, and basic auth endpoints.

## Structure

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

## Quick start

1) Create a .env file based on .env.example.
2) Install dependencies: pip install -e .[dev]
3) Run the API: uvicorn app.main:app --reload

## Docker

docker compose up --build

## Tests

pytest
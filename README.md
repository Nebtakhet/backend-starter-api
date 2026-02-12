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
	<a href="#-features">Features</a>
	·
	<a href="#-prerequisites">Prerequisites</a>
	·
	<a href="#-installation">Installation</a>
	·
	<a href="#-running-the-application">Running</a>
	·
	<a href="#-development-workflow">Development</a>
	·
	<a href="#-api-documentation">API Docs</a>
	·
	<a href="#-docker">Docker</a>
</p>

## ✨ Features

- **FastAPI** app scaffolded for growth with modular services, schemas, and API routers
- **SQLAlchemy 2.0** models with **Alembic** migrations
- **JWT authentication** with refresh token rotation and reuse detection
- **Rate limiting** on auth endpoints
- **Items CRUD** with ownership enforcement
- Comprehensive **test suite** with pytest
- **CI pipeline** with GitHub Actions (lint, format, typecheck, tests)
- **Pre-commit hooks** for local quality enforcement

## 🧭 Project Structure

```text
backend-starter-api/
├── app/
│   ├── main.py              # FastAPI app, middleware, exception handlers
│   ├── api/                 # API routes (v1)
│   │   ├── deps.py          # Shared dependencies (get_db, get_current_user)
│   │   └── v1/endpoints/    # Auth, users, items endpoints
│   ├── core/                # Config, security, logging, rate limiting
│   ├── db/                  # Database session, models, base
│   ├── schemas/             # Pydantic schemas for validation
│   ├── services/            # Business logic layer
│   └── utils/               # Utilities
├── tests/                   # Test suite
├── alembic/                 # Database migrations
├── .github/workflows/       # CI/CD pipelines
├── pyproject.toml           # Project metadata and dependencies
├── docker-compose.yml       # Docker orchestration
└── Dockerfile               # Container image definition
```

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.11 or higher** installed
- **pip** and **venv** (usually included with Python)
- **Git** for version control

### Optional
- **PostgreSQL** (for production-like local development)
- **Docker** and **Docker Compose** (for containerized deployment)

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Nebtakhet/backend-starter-api.git
cd backend-starter-api
```

### 2. Create and activate a virtual environment

**On Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

This installs:
- **Runtime dependencies**: FastAPI, SQLAlchemy, JWT libraries, etc.
- **Development tools**: pytest, ruff, mypy, pre-commit

### 4. Set up pre-commit hooks

```bash
pre-commit install
```

Pre-commit hooks automatically run `ruff` (lint + format) on staged files before each commit.

### 5. Configure environment variables

Copy the example environment file and edit it:

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
- `SECRET_KEY` - Use a strong random string (32+ characters)
- `REFRESH_TOKEN_SECRET` - Another strong random string
- `SQLALCHEMY_DATABASE_URI` - Database connection string

**Generate secure keys:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Database connection strings:**
- SQLite (development): `sqlite:///./app.db`
- PostgreSQL: `postgresql://user:password@localhost:5432/dbname`

### 6. Initialize the database

Apply migrations to create tables:

```bash
alembic upgrade head
```

## 🚀 Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health

## 🔧 Development Workflow

### Database Migrations

Create a new migration after modifying models:

```bash
alembic revision --autogenerate -m "description of changes"
```

Apply pending migrations:

```bash
alembic upgrade head
```

### Running Tests

Run the test suite:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=app --cov-report=html
```

### Quality Checks

**Lint and format:**
```bash
ruff check .          # Check for issues
ruff check . --fix    # Auto-fix issues
ruff format .         # Format code
```

**Type checking:**
```bash
mypy app tests
```

**Pre-commit (run all checks manually):**
```bash
pre-commit run --all-files
```

The CI pipeline automatically runs all these checks on every push and pull request.

## 🐳 Docker

### Quick Start

Build and run with Docker Compose:

```bash
docker compose up --build
```

The API will be available at http://localhost:8000

### Running Tests in Docker

```bash
docker compose run --rm --no-deps -e SQLALCHEMY_DATABASE_URI=sqlite:///./test.db api sh -c "pip install -e '.[dev]' && python -m pytest"
```

**Note**: Tests default to SQLite via environment overrides in [tests/conftest.py](tests/conftest.py).

## 📚 API Documentation

### Authentication Flow

1. **Register** a user: `POST /api/v1/users`
2. **Login**: `POST /api/v1/auth/login` → Receive access + refresh tokens
3. **Access protected endpoints** using access token in `Authorization: Bearer <token>` header
4. **Refresh** tokens: `POST /api/v1/auth/refresh` → Rotates refresh token
5. **Logout**: `POST /api/v1/auth/logout` → Revokes refresh token

### Available Endpoints

**Auth:**
- `POST /api/v1/auth/login` - Login with email and password
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Revoke refresh token

**Users:**
- `POST /api/v1/users` - Register a new user
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/me` - Get current user profile

**Items** (authentication required):
- `POST /api/v1/items` - Create a new item
- `GET /api/v1/items` - List user's items
- `GET /api/v1/items/{item_id}` - Get item by ID
- `PUT /api/v1/items/{item_id}` - Update an item
- `DELETE /api/v1/items/{item_id}` - Delete an item

**Health:**
- `GET /health` - Health check endpoint

### Error Format

All errors follow a consistent format:

```json
{
  "detail": "Error message",
  "code": "error_code",
  "errors": [...]
}
```

Error codes:
- `validation_error` - Request validation failed
- `auth_error` - Authentication/authorization failed
- `db_integrity_error` - Database constraint violation
- `db_error` - General database error

## ⚙️ Configuration

### Environment Variables

The following environment variables must be set in your `.env` file:

**Required:**
- `PROJECT_NAME` - Application name
- `SECRET_KEY` - Secret key for JWT access tokens (min 32 characters)
- `REFRESH_TOKEN_SECRET` - Secret key for refresh tokens (min 32 characters)
- `JWT_ISSUER` - JWT issuer claim (default: `backend-starter-api`)
- `JWT_AUDIENCE` - JWT audience claim (default: `backend-starter-api`)
- `CLOCK_SKEW_SECONDS` - Allowed clock skew for JWT validation (default: `30`)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Access token lifetime (default: `60`)
- `AUTH_LOGIN_RATE_LIMIT` - Rate limit for login endpoint (default: `5/minute`)
- `AUTH_REFRESH_RATE_LIMIT` - Rate limit for refresh endpoint (default: `10/minute`)
- `SQLALCHEMY_DATABASE_URI` - Database connection string

**Optional:**
- `REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token lifetime (default: `30`)
- `ENVIRONMENT` - Environment name (default: `development`)

### Security Notes

- Never commit `.env` files to version control
- Use strong, randomly generated keys for `SECRET_KEY` and `REFRESH_TOKEN_SECRET`
- In production, use PostgreSQL instead of SQLite
- The app validates that secret keys are not set to default values in production

## 📄 License

See [LICENSE](LICENSE)

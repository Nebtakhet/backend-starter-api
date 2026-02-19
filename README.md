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
	<a href="#-project-status">Project Status</a>
	·
	<a href="#-prerequisites">Prerequisites</a>
	·
	<a href="#-local-setup-venv">Local Setup</a>
	·
	<a href="#-running-the-application">Running</a>
	·
	<a href="#-testing">Testing</a>
	·
	<a href="#-quality-checks">Quality Checks</a>
	·
	<a href="#-api-documentation">API Docs</a>
	·
	<a href="#-docker">Docker</a>
	·
	<a href="#-configuration">Configuration</a>
</p>

## ✨ Features

- **FastAPI** app scaffolded for growth with modular services, schemas, and API routers
- **SQLAlchemy 2.0** models with **Alembic** migrations
- **JWT authentication** with refresh token rotation and reuse detection
- **Rate limiting** on auth endpoints
- **Items CRUD** with ownership enforcement
- **Pagination** on list endpoints with total counts
- **Health check** with database connectivity status
- **CORS** support configurable via environment
- **Timestamps** on core models (`created_at`, `updated_at`)
- **Redis-backed caching** for selected responses
- **Redis-backed rate limiting** storage for multi-instance deployments
- Comprehensive **test suite** with pytest
- **CI pipeline** with GitHub Actions (lint, format, typecheck, security audit, tests)
- **Pre-commit hooks** for local quality enforcement

## 🧪 Project Status

- **Active development**: This is a starter template meant to be customized.
- **Production readiness**: Not production hardened out of the box (review security, config, and scaling needs).
- **Database**: Models are stable; generate Alembic migrations after changes.
- **Caching/rate limiting**: Redis-backed by default; see configuration below.

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
- **Redis** (for caching and rate limit storage; optional for local dev)

## 📦 Local Setup (venv)

### Step 1: Clone the repository

```bash
git clone https://github.com/Nebtakhet/backend-starter-api.git
cd backend-starter-api
```

### Step 2: Create and activate a virtual environment

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### Step 3: Install dependencies

```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

### Step 4: Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:
- `SECRET_KEY` (32+ chars)
- `REFRESH_TOKEN_SECRET` (32+ chars)
- `SQLALCHEMY_DATABASE_URI`

Optional but recommended:
- `REDIS_URL` (default `redis://localhost:6379/0`)
- `CACHE_TTL_SECONDS` (default `30`)

If you do not want Redis locally, set:
```bash
REDIS_URL="memory://"
```

Generate secure keys:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Database examples:
- SQLite: `sqlite:///./app.db`
- PostgreSQL: `postgresql://user:password@localhost:5432/dbname`

### Step 5: Initialize the database

```bash
alembic upgrade head
```

### Step 6: (Optional) Pre-commit hooks

```bash
pre-commit install
```

## 🚀 Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- **Interactive docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc
- **Health check**: http://localhost:8000/health (includes database status)

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

## 🧪 Testing

### Step 1: Ensure required env vars are set

Tests override settings in [tests/conftest.py](tests/conftest.py), but you can still set:

```bash
export SECRET_KEY="test-secret-key-32-chars-min-000000"
export REFRESH_TOKEN_SECRET="test-refresh-secret-32-chars-0000"
export SQLALCHEMY_DATABASE_URI="sqlite:///./test.db"
export REDIS_URL="memory://"
```

### Step 2: Run tests

```bash
pytest
```

Coverage report:
```bash
pytest --cov=app --cov-report=html
```

## ✅ Quality Checks

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

**Security audit:**
```bash
pip-audit             # Scan for known CVEs in dependencies
```

**Pre-commit (run all checks manually):**
```bash
pre-commit run --all-files
```

The CI pipeline automatically runs all these checks (lint, format, typecheck, security audit, and tests) on every push and pull request.

## 🐳 Docker

### Quick Start (Docker Compose)

Step 1: Start the stack

```bash
docker compose up --build
```

Step 2: Verify the API is healthy

```bash
curl http://localhost:8000/health
```

Step 3: Open docs

- http://localhost:8000/docs

Redis is included in the compose stack for caching and rate limiting.

### Full Compose Run

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
- `GET /api/v1/items` - List user's items (paginated)
- `GET /api/v1/items/{item_id}` - Get item by ID
- `PUT /api/v1/items/{item_id}` - Update an item
- `DELETE /api/v1/items/{item_id}` - Delete an item

**Health:**
- `GET /health` - Health check endpoint (includes database status)

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

## 🏗️ Design & Architecture

### JWT + Refresh Token Strategy

This app uses **JWT access tokens** (short-lived) and **refresh tokens** (long-lived) because:

- **Stateless auth**: No server-side session storage needed. Access token is verified with just the secret key.
- **Scalability**: Any server can validate the token without checking a session store; perfect for distributed systems.
- **Short expiry**: Access tokens expire quickly (60 min default), limiting damage from token theft.
- **Refresh rotation**: Refresh tokens are rotated on every refresh, and old ones are invalidated if reused (detects token theft).

**Why refresh tokens are hashed in the database:**
- If the DB is compromised, attackers can't directly use the leaked tokens (hashes are one-way).
- When a refresh token is used, we compare the incoming token's hash to the stored hash; they match only if it's the legitimate token.

### Ownership Enforcement

Items belong to users. The API enforces ownership at the service layer:

```python
db.query(Item).filter(Item.owner_id == current_user.id).all()
```

This prevents users from accessing/modifying other users' items—a fundamental multi-tenant security pattern. Without it, any authenticated user could modify anyone's data.

### Service Layer vs API Layer

- **API layer** (`app/api/`): Handles HTTP routing, request validation, and response serialization.
- **Service layer** (`app/services/`): Contains business logic, DB queries, and invariant enforcement (e.g., ownership checks). Reusable.

Separation of concerns makes the codebase testable and maintainable. If you add a CLI or gRPC endpoint later, reuse the service layer without duplicating logic.

### Scaling Architecture

This template is **stateless by design**, ready to scale:

```
┌─────────────────────────────────────┐
│    Load Balancer (nginx, etc)       │
├─────────────────────────────────────┤
│ API Server 1 │ API Server 2 │ ... │  ← Stateless (no session affinity needed)
├─────────────────────────────────────┤
│           PostgreSQL Database       │  ← Persistent data (queries, auth)
├─────────────────────────────────────┤
│  Redis/Memcached (optional)         │  ← Cache layer for expensive queries
│     Celery/RQ (optional)            │  ← Async job queue for long operations
└─────────────────────────────────────┘
```

**Why this works:**
- JWT tokens don't require session affinity; any server can validate them.
- Database is the single source of truth.
- Caching (Redis) speeds up frequent queries.
- Job queues (Celery) handle async work (e.g., sending emails).

To scale: add more API servers behind a load balancer, and upgrade the DB to a managed service (AWS RDS, Heroku Postgres, etc).

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
- `CORS_ORIGINS` - JSON array of allowed origins (default: `http://localhost:3000`, `http://localhost:5173`)
- `REDIS_URL` - Redis connection string (default: `redis://localhost:6379/0`)
- `CACHE_TTL_SECONDS` - Default response cache TTL (default: `30`)

### Security Notes

- Never commit `.env` files to version control
- Use strong, randomly generated keys for `SECRET_KEY` and `REFRESH_TOKEN_SECRET`
- In production, use PostgreSQL instead of SQLite
- The app validates that secret keys are not set to default values in production

## 📄 License

See [LICENSE](LICENSE)

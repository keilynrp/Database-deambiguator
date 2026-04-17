# Contributing

Thank you for your interest in contributing to **UKIP — Universal Knowledge Intelligence Platform**!

## Development Setup

Recommended local workflow:

- use `start.bat` for day-to-day Windows development
- use Docker Compose primarily for PostgreSQL, staging validation, and deployment-oriented testing

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+

### Backend

```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.lock

# Optional for PDF export on Windows:
# install the GTK runtime required by WeasyPrint
# (or run PDF export from Docker / Linux)

# Start local PostgreSQL
docker compose -f docker-compose.dev.yml up -d postgres

# Apply schema migrations
alembic upgrade head

# Start the API server
uvicorn backend.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3004` and the backend at `http://localhost:8000`.

### Windows fast path

For the usual local development loop on Windows, prefer:

```bat
start.bat
```

Useful restart modes:

```bat
start.bat restart-backend
start.bat restart-frontend
start.bat restart-all
```

### Docker workflow

When you want the full stack in containers for staging, deployment validation, or production-like runs:

```bash
cp .env.example .env
docker compose up -d --build
```

Use the Docker-specific variables for container networking:

- `DOCKER_DATABASE_URL`
- `DOCKER_POSTGRES_HOST`
- `DOCKER_POSTGRES_PORT`
- `DOCKER_POSTGRES_DB`
- `DOCKER_POSTGRES_USER`
- `DOCKER_POSTGRES_PASSWORD`
- `DOCKER_FRONTEND_API_URL`

Do not point container services at `127.0.0.1` unless you intentionally mean the container itself.

Rebuild guidance:

- backend code or backend image inputs changed:
  - `docker compose up -d --build ukip-backend`
- frontend code or `NEXT_PUBLIC_*` build args changed:
  - `docker compose up -d --build ukip-frontend`
- runtime env only changed:
  - `docker compose up -d --force-recreate <service>`

PDF export note:
- `weasyprint` is included in `requirements.lock`, but on Windows it also needs native GTK libraries.
- If `/exports/pdf` reports missing runtime libraries, install the GTK runtime and restart the backend, or use Docker/Linux for PDF generation.

## Project Structure

```
ukip/
├── backend/          # FastAPI application
│   ├── main.py       # API routes and business logic
│   ├── models.py     # SQLAlchemy ORM models
│   ├── schemas.py    # Pydantic validation schemas
│   └── database.py   # Database engine configuration
├── frontend/         # Next.js application
│   └── app/          # App Router pages and components
├── scripts/          # Utility CLI scripts
├── data/             # Data files (gitignored .xlsx)
├── docs/             # Documentation
├── requirements.txt  # Human-maintained dependency intent
└── requirements.lock # Reproducible backend install lockfile
```

## Code Style

### Backend (Python)

- Follow PEP 8 conventions.
- Use type hints where practical.
- Keep endpoints in `main.py` unless the file grows significantly.

### Frontend (TypeScript / React)

- Use functional components with hooks.
- Follow the existing Tailwind CSS patterns (rounded-2xl cards, consistent color palette).
- Place reusable components in `frontend/app/components/`.
- Page routes go in their own directory under `frontend/app/`.

## Making Changes

1. Create a branch from `main`.
2. Make your changes with clear, descriptive commits.
3. Test both backend and frontend manually:
   - Backend: verify endpoints via `http://localhost:8000/docs` (Swagger UI).
   - Frontend: navigate through all pages and verify functionality.
4. Open a pull request with a summary of what changed and why.

## Reporting Issues

Open an issue on GitHub with:
- Steps to reproduce the problem.
- Expected vs actual behavior.
- Browser / OS / Python / Node versions if relevant.

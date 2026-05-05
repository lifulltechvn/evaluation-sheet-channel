# Database Migrations (Alembic)

Migrations run **automatically** on `docker compose up` via Alembic before the backend starts.

## How it works

```
docker compose up
  └─ postgres (healthcheck passes)
       └─ backend entrypoint.sh
            ├─ alembic upgrade head   ← runs all pending migrations
            └─ uvicorn main:app       ← starts the API
```

## File structure

```
backend/
├── alembic.ini                          # Alembic config (reads DATABASE_URL from env)
├── alembic/
│   ├── env.py                           # SQLAlchemy connection setup
│   ├── script.py.mako                   # Template for new revisions
│   └── versions/
│       └── 0001_init_schema_and_seed_data.py
├── models.py                            # SQLAlchemy ORM models
└── entrypoint.sh                        # alembic upgrade head → uvicorn
```

## Adding a new migration

```bash
# Inside the backend container (or local venv with DATABASE_URL set)
alembic revision --autogenerate -m "add column foo to users"
# Edit the generated file in alembic/versions/, then commit it.
```

Teammates get the migration automatically on next `docker compose up`.

## Reset the database

```bash
docker compose down -v   # removes the postgres_data volume
docker compose up        # re-runs all migrations from scratch
```

## Connect locally

```
Host:     localhost
Port:     5432
Database: company_evaluation
User:     postgres
Password: postgres
```

## Schema overview

| Table                | Description                                      |
|----------------------|--------------------------------------------------|
| `roles`              | Permission roles (CEO, HR, Manager, …)           |
| `teams`              | Org structure — UNITs contain GROUPs             |
| `users`              | Employees with role / team / manager             |
| `evaluation_periods` | A named evaluation period (e.g. Q1 2026)         |
| `templates`          | Google Sheet template files                      |
| `evaluations`        | One evaluation record per employee per period    |
| `audit_logs`         | Immutable action log                             |

# Evaluation Sheet Channel

AI-powered evaluation sheet management system — Team Channel, AI Contest 2026.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose
- Google Cloud Service Account (for Google Drive integration)

## Quick Start

### 1. Setup Google Drive credentials

Create `backend/credentials.json` with your Google Cloud Service Account key:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-bot@your-project.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",
  "universe_domain": "googleapis.com"
}
```

### 2. Setup Shared Drive

1. Create a **Shared Drive** on Google Drive
2. Add the service account email (from `client_email` above) as **Contributor**
3. Upload 3 evaluation template spreadsheets into the Shared Drive
4. Create period folders (e.g., `PERIOD_2026_Q1`, `PERIOD_2026_Q2`) in the Shared Drive
5. Update IDs in `backend/alembic/versions/0001_init_schema_and_seed_data.py`:
   - `templates` → `google_file_id` = spreadsheet file IDs
   - `evaluation_periods` → `folder_id` = folder IDs

### 3. Run

```bash
docker compose up --build
```

- **Frontend (HR Dashboard):** http://localhost:3000
- **Backend API (Swagger docs):** http://localhost:8000/docs

## Project Structure

```
backend/     # Python FastAPI — REST API + Alembic migrations
frontend/    # Next.js — HR Dashboard UI
```

## Architecture

- **Database:** PostgreSQL (auto-migrated via Alembic on startup)
- **Google Drive:** Service Account + Shared Drive (copy template spreadsheets per employee)
- **Auth:** JWT-based (login with email/password)

## Demo Flow

1. Open http://localhost:3000, login with `sondv@lifull.com` / `sondv@123` (CEO)
2. Click **Generate All Sheets** — creates evaluation spreadsheets for all employees (with live progress bar via SSE)
3. Go to **Sheets** tab → use **Send** / **Validate** buttons per sheet
4. Go to **Employees** tab → click **History** to view past evaluations
5. Use **Send Results Email** or **Migrate from 2025-H2** on the Dashboard

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JWT_SECRET_KEY` | (set in docker-compose) | Secret for JWT token signing |
| `DATABASE_URL` | (set in docker-compose) | PostgreSQL connection string |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | `/app/credentials.json` | Path to service account JSON |
| `BACKEND_URL` | `http://backend:8000` | Backend URL (used by Next.js proxy) |

## Stop

```bash
docker compose down        # keep data
docker compose down -v     # reset database
```

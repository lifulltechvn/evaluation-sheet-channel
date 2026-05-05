# Evaluation Sheet Channel

AI-powered evaluation sheet management system — Team Channel, AI Contest 2026.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & Docker Compose

## Quick Start

```bash
docker compose up -d --build
```

- **Frontend (HR Dashboard):** http://localhost:3000
- **Backend API (Swagger docs):** http://localhost:8000/docs

## Project Structure

```
backend/     # Python FastAPI — REST API
frontend/    # Next.js — HR Dashboard UI
```

## Demo Notes

Third-party services (Google Sheets, OpenAI, Gmail) are mocked with in-memory data. 5 sample employees are pre-loaded.

### Demo Flow

1. Open http://localhost:3000
2. Click **Generate All Sheets** to create evaluation sheets for all employees
3. Go to **Sheets** tab → use **Send** / **Validate** buttons per sheet
4. Go to **Employees** tab → click **History** to view past evaluations
5. Use **Send Results Email** or **Migrate from 2025-H2** on the Dashboard

## Stop

```bash
docker compose down
```

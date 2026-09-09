# Production URL Shortener

Python/FastAPI. Short codes are stored in **PostgreSQL**, so they survive restarting uvicorn.

## Prerequisites

- Python 3.12+
- PostgreSQL running locally, with a database (for example `urls`)

Create the database once (password prompt is for the `postgres` user):

```powershell
psql -U postgres -c "CREATE DATABASE urls;"
```

## Environment

Copy this into a `.env` file in the project root (do not commit `.env`):

```text
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/urls
```

The app loads `.env` on startup. `DATABASE_URL` is the connection string (user, password, host, port, database name).

On first start, the app runs `CREATE TABLE IF NOT EXISTS` for table `urls` (`code`, `original_url`, `created_at`).

## Run locally (PowerShell)

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

`source` is for bash. On Windows PowerShell, use `Activate.ps1`.

`uvicorn app.main:app` means: import `app` from `app/main.py`. `uvicorn main:app` fails because there is no `main.py` at the repo root.

Stop the server with Ctrl+C.

## API

- `GET http://127.0.0.1:8000/health` → `{"status": "ok"}` (process is up; it does not prove Postgres is healthy)
- `POST http://127.0.0.1:8000/urls?url=https://example.com` → JSON with `code`, `short_url`, `original_url`
- `GET http://127.0.0.1:8000/{code}` → `302` to the original URL, or `404`

`/docs` is useful for POST. Redirects in `/docs` may show “Failed to fetch” (browser CORS after 302). Use the address bar or copy-paste the code instead.

Prove durability: POST, restart uvicorn, GET the same code — still 302.
